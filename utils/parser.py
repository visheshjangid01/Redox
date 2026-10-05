import re, json
from utils.tools import Tools, Splitter
from utils.reserved import Operators
from memory import Env, glob, Block
class Parser:
    """
    - val: convert string values to their proper datatypes
    - brackets: convert string values to
    """

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

    def val(self, value, next_value=None, env=glob):
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
            if value == "out^":
                print(*fields)
                return 'None^'
            return globals()[value](*fields)

        if self.VAR_RE.match(value):
            if next_value in Operators.assignment:
                return "$" + value
            return env.get_var(value)

        if Tools.contains(value, '{', '}'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return self.brackets(value, '{}')

        if Tools.contains(value, '[', ']'):
            return self.brackets(value, '[]')

        if  Tools.contains(value, '(', ')'):
            return self.brackets(value, '()')

        return value

    @staticmethod
    def brackets( value: str, bracket_type: str):
        from utils.depopulate import Depopulate
        line = value[1:-1]
        comps = Depopulate().bracket(line)
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
        name = name[1:]
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
                value = self.operator(op, env.get_var(name), value)
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
                return None

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

    @staticmethod
    def line(lines: list):
        result = []
        block = None
        global_prev = None

        for line in lines:

            comps = Splitter().split(line)

            if not comps:
                continue

            # Handle Block Closure
            if block:
                # Check if the line starts with whitespace tokens
                is_indented = isinstance(comps[0], str) and comps[0].isspace()
                pref = comps[0] if is_indented else ""

                if not is_indented:
                    block.ended = True
                else:
                    if not block.prefix:
                        block.prefix = pref
                    if len(pref) < len(block.prefix):
                        block.ended = True

                # Resolve potentially multiple nested blocks ending
                while block and block.ended:
                    if block.parent:
                        block.parent.add(block)
                    else:
                        result.append(block)
                        global_prev = block

                    block = block.parent

                    # Evaluate if the newly active parent block also ends on this line
                    if block:
                        if not is_indented:
                            block.ended = True
                        elif block.prefix and len(pref) < len(block.prefix):
                            block.ended = True
                        else:
                            break

                if block and is_indented and isinstance(comps[0], str) and comps[0].isspace():
                    comps.pop(0)
            elif comps and isinstance(comps[0], str) and comps[0].isspace():
                comps.pop(0)

            if isinstance(comps, list) and comps and comps[-1] == ":":
                if block:
                    current_prev = block.body[-1] if block.body else None
                    block_env = block.env
                else:
                    current_prev = global_prev
                    block_env = glob

                block = Block(comps, block, current_prev, block_env)
                continue

            if block:
                block.add(comps)
            else:
                result.append(comps)
                global_prev = comps

        # Take care of  block or multiple blocks if there are any at end of file
        while block:
            block.ended = True
            if block.parent:
                block.parent.add(block)
            else:
                result.append(block)
                global_prev = block
            block = block.parent

        return result