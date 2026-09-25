from utils.tools import Splitter, Tools
from utils.parser import Parser

class Depopulate:
    """
    Methods:
    - evaluate: operators in proper order provided by order method in Tools class
    """
    invalids = [',']

    def all(self, line: str, invalid=None) -> list:
        if invalid is None:
            invalid = self.invalids
        comps = Splitter().split(line, invalid)
        out = []
        skip = False
        for i, comp in enumerate(comps, start=1):
            if skip:
                skip = False
                continue

            if comp in invalid:
                raise SyntaxError(f"Invalid character: {comp}")
            next_comp = comps[i] if i < len(comps) else None
            value = Parser().val(comp, next_comp)
            if value != "None^":
                out.append(value)
            if comp.endswith("^"):
                skip = True
        return out

    def bracket(self, line: str) -> list:
        invalid = [
            # Operators
            '=>', '->', ':', ''
        ]
        return self.all(line, invalid)

    @staticmethod
    def evaluate(comps):
        if not comps:
            return None
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