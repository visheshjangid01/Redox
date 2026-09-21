import re, json
from memory import glob, Env

FLOAT_RE = re.compile(r"-?\d+\.\d+")
INT_RE = re.compile(r"-?\d+")
# Starts with alphabet then can contain alphanum, - and _
VAR_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

BOOLEAN_MAP = {
    "true": True, "false": False, "null": None,
    "t": True, "f": False, "n": None
}


def val(value, env=glob):
    if not isinstance(value, str):
        return value

    if value.startswith("'") or value.startswith('"'):
        return value

    if value in BOOLEAN_MAP:
        return BOOLEAN_MAP[value]

    if FLOAT_RE.fullmatch(value):
        return float(value)

    if INT_RE.fullmatch(value):
        return int(value)

    if VAR_RE.match(value):
        return val(env.get_var(value))

    if value.startswith("{") and value.endswith("}"):
        return json.loads(value)

    if value.startswith("[") and value.endswith("]"):

        return [val(item) for item in value[1:-1].split(",")]

    return None


def operator(op, first, second):
    first = val(first)
    second = val(second)

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