import re, json
from time import struct_time

from reserved import Operators
from memory import glob, Env

"""
- val: convert string values to their proper datatypes
- brackets: convert string values to 
"""
class Parser:
    FLOAT_RE = re.compile(r"-?\d+\.\d+")
    INT_RE = re.compile(r"-?\d+")
    # Starts with alphabet then can contain alphanum, - and _
    VAR_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
    FUNC_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*\^$")

    BOOLEAN_MAP = {
        "true": True, "false": False, "null": None,
        "t": True, "f": False, "n": None
    }

    NONE_MAP = ['None', 'none', 'null', 'nil' ]

    def val(self, value, next_value):
        if not isinstance(value, str):
            return value

        # Does nothing if value is a string or a variable
        if Tools.contains(value, '"','"') or Tools.contains(value, "'","'")  or value.startswith("$"):
            return value

        if value in self.NONE_MAP:
            return None

        if value in self.BOOLEAN_MAP:
            return self.BOOLEAN_MAP[value]

        if self.FLOAT_RE.fullmatch(value):
            return float(value)

        if self.INT_RE.fullmatch(value):
            return int(value)

        if self.FUNC_RE.match(value):
            fields = self.brackets(next_value, '^')
            return fields

        if self.VAR_RE.match(value):
            return f"${value}"


        if Tools.contains(value, '{', '}'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return self.brackets(value, '{}')

        if Tools.contains(value, '[', ']'):
            return self.brackets(value, '[]')

        if  Tools.contains(value, '(', ')'):
            return self.brackets(value, '()')

        raise ValueError(f"Invalid value type: {value}")

    @staticmethod
    def brackets( value: str, bracket_type: str):
        line = value[1:-1]
        comps = Splitter().bracket(line)
        block, values = [], []
        for comp in comps:
            if comp == ',':
                values.append(Depopulate.evaluate(block))
                block = []
                continue
            block.append(comp)
        else:
            values.append(Depopulate.evaluate(block))
        match bracket_type:
            case "[]":
                return values
            case "{}":
                return set(values)
            case "()":
                if len(values) == 1:
                    return values[0]
                return tuple(values)
            case "^": # Special case for function brackets
                return tuple(values)
            case _:
                return values

    def define_var(self, name: str, value, op: str, env: Env) -> bool:
        if not name.startswith("$"):
            return False
        if op in Operators.assignment:
            if op == "->":
                env.set_var(name, value)
            elif op == "=>":
                env.set_var(name, value, False)
            else:
                if op == "-->":
                    op = "-"
                else:
                    op = op[:-1]
                value = self.operator(op, name, value)
                env.set_var(name, value)
            return True
        return False

    def operator(self, op: str, first, second, env=glob):

        # No longer relevant as value-type is handled byt splitter itself
        # first = self.val(first)
        # second = self.val(second)
        # if isinstance(zero, str):

        # If its an assignment operator it will assign the value and return None as an indicator
        if isinstance(first, str):
            if self.define_var(first, value=second, op=op, env=env):
                return "defined*"

        t1, t2 = type(first), type(second)

        match op:
            case "=":
                return first == second
            case "!=":
                return first != second
            case ">":
                try:
                    return first > second
                except TypeError:
                    raise TypeError(f"Cannot compare {t1.__name__} and {t2.__name__} using '>'")
            case "<":
                try:
                    return first < second
                except TypeError:
                    raise TypeError(f"Cannot compare {t1.__name__} and {t2.__name__} using '<'")
            case ">=":
                try:
                    return first >= second
                except TypeError:
                    raise TypeError(f"Cannot compare {t1.__name__} and {t2.__name__} using '>='")
            case "<=":
                try:
                    return first <= second
                except TypeError:
                    raise TypeError(f"Cannot compare {t1.__name__} and {t2.__name__} using '<='")

            case "+":
                if isinstance(first, dict) and isinstance(second, dict):
                    return {**first, **second}


                if isinstance(first, str) or isinstance(second, str):
                    return str(first) + str(second)

                try:
                    return first + second
                except TypeError:
                    pass

            case "-":
                if isinstance(first, list) and isinstance(second, list):
                    return [x for x in first if x not in second]
                if isinstance(first, tuple) and isinstance(second, tuple):
                    return tuple(x for x in first if x not in second)
                if isinstance(first, dict):
                    if isinstance(second, dict):
                        return {k: v for k, v in first.items() if k not in second}
                    return {k: v for k, v in first.items() if k != second}
                try:
                    return first - second
                except TypeError:
                    pass

            case "*":
                try:
                    return first * second
                except TypeError:
                    pass

            case "/":
                if second == 0: raise ZeroDivisionError("division by zero")
                try:
                    return first / second
                except TypeError:
                    pass

            case "//":
                if second == 0: raise ZeroDivisionError("integer division or modulo by zero")
                try:
                    return first // second
                except TypeError:
                    pass

            case "%":
                if second == 0: raise ZeroDivisionError("modulo by zero")
                try:
                    return first % second
                except TypeError:
                    pass

            case "^":
                if isinstance(first, (int, float, bool)) and isinstance(second, (int, float, bool)):
                    return first ** second

            case "|":
                try:
                    return first | second
                except TypeError:
                    pass

            case "&":
                if isinstance(first, dict) and isinstance(second, dict):
                    return {k: first[k] for k in first if k in second}
                try:
                    return first & second
                except TypeError:
                    pass

            case _:
                raise SyntaxError(f"Unknown operator {op}")

        raise TypeError(f"Unsupported '{op}' operation between {t1.__name__} and {t2.__name__}")

class Splitter:
    """
    splits components of a block into raw elements/components
    """
    @staticmethod
    def splitter(line: str, invalid: list) -> list:
        p1, p2, char_count, bracket_level = 0, 0, 0, 0
        comment = "#"
        symbols = ['>', '<', '=', '-', '+', ':', '|', '/', '%', '!', '*', ',']
        comps = []
        quote = None # to detect and build string
        temp_op = ''
        while p2 < len(line):

            char = line[p2]
            if not quote:
                if char == comment:
                    break
                # increase bracket level and split if not
                if char in ['(', '{', '[']:
                    # " nums(", " ((", "nums{}"
                    if char_count > 0 and bracket_level == 0:
                        char_count = 0
                        comps.append(line[p1:p2])
                        p1 = p2
                    if line[p2 - 1].isalnum() and char != '{':

                        if comps:
                            comps.append(comps.pop(-1) + "^")
                    p2 += 1
                    bracket_level += 1
                    continue
                elif char in [')', '}', ']']:
                    bracket_level -= 1
                    p2 += 1
                    continue

            if not quote and bracket_level == 0:
                # ignore comments
                if char == comment:
                    break

                # break on space, ignore if no text behind
                if char == " ":
                    if char_count > 0:
                        comps.append(line[p1:p2])
                        char_count = 0
                    p1 = p2 + 1
                    p2 += 1
                    continue

                loop_executed = False
                # build the operator
                while char in symbols and p2 < len(line):
                    loop_executed = True
                    temp_op += char
                    if char_count > 0:
                        comps.append(line[p1:p2])
                        char_count = 0
                    p2 += 1
                    try:
                        char = line[p2]
                    except IndexError:
                        char = ''
                # insert the operator in components once the loop end
                if loop_executed:
                    comps.append(temp_op)
                    temp_op = ''
                    p1 = p2
                    continue

            if char.isalnum():
                char_count += 1
            elif char in ('"', "'"):
                if char == quote:
                    quote = None
            p2 += 1

        if char_count > 0:
            comps.append(line[p1:])

        out = []
        skip = False
        for i, comp in enumerate(comps, start=1):
            if skip:
                skip = False
                continue

            if comp in invalid:
                raise SyntaxError(f"Invalid character: {comp}")
            try:
                if comp.endswith("^"):
                    out.append(comp)
                    skip = True
                out.append(Parser().val(comp, comps[i]))
            except ValueError:
                out.append(comp)
            except IndexError:
                out.append(Parser().val(comp, None))

        return out

    def raw(self, line: str) -> list:
        invalid = [',']
        return self.splitter(line, invalid)

    def bracket(self, line: str) -> list:
        invalid = [
            # Operators
            '=>', '->', ':', ''
        ]
        return self.splitter(line, invalid)
"""
Methods:
- Order: gives correct order of operators to be solved
- is_valid_string: Checks if it is a valid string component
"""
class Tools:
    @staticmethod
    def order(comps):
        temp = comps.copy()
        out = []
        for level, ops in Operators().all.items():
            for item in temp:
                if item in ops:
                    temp.remove(item)
                    out.append(item)
                    continue
        return out

    @staticmethod
    def is_valid_string(value: str) -> bool:
        if not value:
            return False

        is_bracketed = (
                (value.startswith("[") and value.endswith("]")) or
                (value.startswith("{") and value.endswith("}")) or
                (value.startswith("(") and value.endswith(")"))
        )

        has_quote = "'" in value or '"' in value

        return not is_bracketed and has_quote

    @staticmethod
    def contains(value: str, start, end) -> bool:
        return value.startswith(start) and value.endswith(end)

"""
Methods:
- evaluate: operators in proper order provided by order method in Tools class
"""
class Depopulate:
    @staticmethod
    def evaluate(comps):
        od = Tools.order(comps)
        while len(od) > 0:
            op = od.pop(0)
            index = comps.index(op)
            try:
                first, second = comps.pop(index - 1), comps.pop(index)
            except IndexError:
                raise SyntaxError("Invalid Syntax")
            comps[index-1] = Parser().operator(op, first, second)

        out = comps[0]
        if type(out).__name__ == "str":
            if Tools.is_valid_string(out):
                out = out.replace("'", "")
                out = out.replace('"', "")
                return f"'{out}'"
        return out

print("------------- Redox --------------")
while True:
    user = input(">>> ")
    if user == "exit":
        break

print(Depopulate.evaluate("c"))