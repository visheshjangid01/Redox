import re, json
from reserved import operators
from memory import glob, Env

class Parser:

    FLOAT_RE = re.compile(r"-?\d+\.\d+")
    INT_RE = re.compile(r"-?\d+")
    # Starts with alphabet then can contain alphanum, - and _
    VAR_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

    BOOLEAN_MAP = {
        "true": True, "false": False, "null": None,
        "t": True, "f": False, "n": None
    }

    def val(self, value, env=glob):
        if not isinstance(value, str):
            return value

        if value.startswith("'") or value.startswith('"'):
            return value

        if value in self.BOOLEAN_MAP:
            return self.BOOLEAN_MAP[value]

        if self.FLOAT_RE.fullmatch(value):
            return float(value)

        if self.INT_RE.fullmatch(value):
            return int(value)

        if self.VAR_RE.match(value):
            return self.val(env.get_var(value))

        if value.startswith("{") and value.endswith("}"):
            return json.loads(value)

        if value.startswith("[") and value.endswith("]"):

            return [self.val(item) for item in value[1:-1].split(",")]

        return None


    def operator(self, op, first, second):
        first = self.val(first)
        second = self.val(second)

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
        is_string = False
        temp_op = ''
        while p2 < len(line):
            char = line[p2]
            if not is_string:
                if char == comment:
                    break
                # increase bracket level and split if not
                if char in ['(', '{', '[']:
                    bracket_level += 1
                    # " nums(", " ((", "nums{}"
                    if char_count > 0:
                        char_count = 0
                        comps.append(line[p1:p2])
                        p1 = p2
                    if line[p2 - 1].isalnum() and char != '{':
                        comps.append(comps.pop(-1) + "^")

                    p2 += 1
                    continue
                elif char in [')', '}', ']']:
                    bracket_level -= 1
                    p2 += 1
                    continue

            if not is_string and bracket_level == 0:
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
            elif char == "'" or char == '"':
                is_string = not is_string
            p2 += 1
        if char_count > 0:
            comps.append(line[p1:])
        for comp in comps:
            if comp in invalid:
                raise SyntaxError(f"Invalid character {comp}")
        return comps

    def raw(self, line: str) -> list:
        invalid = [',']
        return self.splitter(line, invalid)

    def bracket(self, line: str) -> list:
        invalid = [
            # Operators
            '=>', '->', ';'
        ]
        return self.splitter(line, invalid)

class Tools:
    @staticmethod
    def order(comps):
        temp = comps.copy()
        out = []
        for level, ops in operators.items():
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



    def evaluate(self, comps):
        od = self.order(comps)
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
            if self.is_valid_string(out):
                out = out.replace("'", "")
                out = out.replace('"', "")
                return f"'{out}'"
        return out

    print(evaluate(Splitter().raw("10 + 20 * 10 + 'H'")))