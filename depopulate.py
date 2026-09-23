from parser import val, operator
from reserved import operators
from splitter import raw

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

def evaluate(comps):
    od = order(comps)
    while len(od) > 0:
        op = od.pop(0)
        index = comps.index(op)
        try:
            first, second = comps.pop(index - 1), comps.pop(index)
        except IndexError:
            raise SyntaxError("Invalid Syntax")
        comps[index-1] = operator(op, first, second)

    out = comps[0]
    if type(out).__name__ == "str":
        if is_valid_string(out):
            out = out.replace("'", "")
            out = out.replace('"', "")
            return f"'{out}'"
    return out

print(evaluate(raw("10 + 20 * 10 + 'H'")))