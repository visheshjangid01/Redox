from utils.reserved import Operators, keywords
from utils.tools import Splitter, Tools
from utils.parser import Parser
from memory import glob, Env, Block
class Depopulate:
    """
    Methods:
    - evaluate: operators in proper order provided by order method in Tools class
    """
    invalids = [',']

    def all(self, line, invalid=None, env=glob) -> list:
        if invalid is None:
            invalid = self.invalids
        comps=[]
        if isinstance(line, str):
            comps = Splitter().split(line)

        if isinstance(comps, Block):
            if comps.header[0] in ["if", "elseif", "else"]:
                getattr(Keywords, "key_"+comps.header[0])(comps)
            return []
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

    def line(self, lines: list):
        content = Parser.line(lines)
        for l in content:
            self.all(l)

class Keywords:
    @staticmethod
    def key_if(block: Block):
        invalid = ["if", "else", "elseif", "func"] + Operators.assignment
        condition = block.header[1:-1]
        result = None
        if block.parent:
            result = Depopulate().all(condition, invalid, block.parent.env)
        else:
            result = Depopulate().all(condition, invalid)
        if len(result) > 1:
            raise SyntaxError("Invalid Syntax")
        if result:
            for line in block.body:
                Depopulate().all(line, invalid, env=block.env)
            block.mark()
            return True
        return False

    def key_elseif(self, block: Block):
        if not self.is_valid(["if", "elseif"], block):
            raise SyntaxError("There must be a valid if or elseif before elseif")
        if self.has_ran(["if", "elseif"],block):
            return False
        invalid = ["if", "else", "elseif", "elseif"] + Operators.assignment
        condition = block.header[1:-1]
        result = None
        if block.parent:
            result = Depopulate().all(condition, invalid, block.parent.env)
        else:
            result = Depopulate().all(condition, invalid)
        if len(result) > 1:
            raise SyntaxError("Invalid Syntax")
        if result:
            for line in block.body:
                Depopulate().all(line, env=block.env)
            block.mark()
            return True
        return False

    def key_else(self, block: Block):
        if len(block.header) != 2:
            raise SyntaxError("Invalid Syntax")
        if not self.is_valid(["if", "elseif"], block):
            raise SyntaxError("There must be an if or elseif before else")
        if self.has_ran(["if", "elseif"],block):
            return False
        for line in block.body:
            Depopulate().all(line, env=block.env)
            block.mark()
        return True

    @staticmethod
    def block_exists(t, block: Block) -> bool:
        current = block
        while isinstance(current.previous, Block):
            current = current.previous
            if not isinstance(current, Block):
                return False
            if current.header[0] in t:
                return True
        return False

    @staticmethod
    def is_valid(t, block: Block):
        if isinstance(block.previous, Block):
            return False
        if block.previous.header[0] in t:
            return True
        return False

    @staticmethod
    def has_ran(t, block: Block) -> bool:
        current = block
        while isinstance(current.previous, Block):
            current = current.previous
            if not isinstance(current, Block):
                return False
            if current.header[0] not in t:
                return False
            if current.header[0] == t[0] and not current.ran:
                return False
            if current.ran:
                return True
        return False

# Depopulate.line(["  Hi", "  Hello  "])