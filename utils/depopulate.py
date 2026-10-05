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

    def all(self, comps, invalid=None, env=glob) -> list:
        if invalid is None:
            invalid = self.invalids

        if isinstance(comps, str):
            comps = Splitter().split(comps)
        elif isinstance(comps, Block):
            if comps.header[0] in ["if", "elseif", "else", "loop"]:
                getattr(Keywords, "key_"+comps.header[0])(comps)
            if comps.header[0] in ["while", "for"]:
                raise SyntaxError("Not a valid loop type")
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
            value = Parser().val(comp, next_comp, env=env)
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
    def evaluate(comps, env=glob):
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
            comps[index-1] = Parser().operator(op, first, second, env=env)

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
            self.evaluate(self.all(l))


class Keywords:
    @staticmethod
    def key_loop(block: Block):
        if block.header[1] not in ["while", "for"]:
            raise SyntaxError("Not a valid loop type")
        if getattr(Keywords, "loop_"+block.header[1])(block):
            return True
        return False

    @staticmethod
    def loop_for(block: Block):
        if not block.header[2]:
            raise SyntaxError("No iterable component available")

        parent_env = block.parent.env if block.parent else glob
        iterables = Depopulate().evaluate(Depopulate().all(block.header[2], env=parent_env), env=parent_env)
        if not isinstance(iterables, (list, tuple, set)):
            raise SyntaxError("Non iterable component!")
        if block.header[3] == ":":
            for i in iterables:
                for line in block.body:
                    Depopulate.evaluate(Depopulate().all(line, env=block.env), env=block.env)
        elif block.header[3] == "as":
            if not Parser.VAR_RE.match(block.header[4]):
                raise SyntaxError("Invalid Loop variable")
            if block.header[5] != ":":
                raise SyntaxError("Invalid Syntax")
            env = block.parent.env if block.parent else glob

            for item in iterables:
                env.set_var(block.header[4], item)
                for line in block.body:
                    Depopulate.evaluate(Depopulate().all(line, env=block.env), env=block.env)
        else:
            raise SyntaxError("Invalid Syntax")

    @staticmethod
    def loop_while(block: Block):
        invalid = ["if", "else", "elseif", "func"] + Operators.assignment
        condition = block.header[2:-1]

        while True:

            raw_cond = Depopulate().all(condition, invalid, env=block.env)
            result = Depopulate.evaluate(raw_cond, env=block.env)

            if not result:
                break

            for line in block.body:
                Depopulate.evaluate(Depopulate().all(line, env=block.env), env=block.env)
        return True
    @staticmethod
    def key_if(block: Block):
        invalid = ["if", "else", "elseif", "func"] + Operators.assignment
        condition = block.header[1:-1]

        raw_cond = Depopulate().all(condition, invalid, env=block.env)
        result = Depopulate.evaluate(raw_cond, env=block.env)

        if result:
            for line in block.body:
                Depopulate.evaluate(Depopulate().all(line, env=block.env), env=block.env)
            block.mark()
            return True
        return False

    @staticmethod
    def key_elseif(block: Block):
        if not Keywords.is_valid(["if", "elseif"], block):
            raise SyntaxError("There must be a valid if or elseif before elseif")
        if Keywords.has_ran(["if", "elseif"], block):
            return False

        invalid = ["if", "else", "elseif", "elseif"] + Operators.assignment
        condition = block.header[1:-1]

        raw_cond = Depopulate().all(condition, invalid, env=block.env)
        result = Depopulate.evaluate(raw_cond, env=block.env)

        if result:
            for line in block.body:
                Depopulate.evaluate(Depopulate().all(line, env=block.env), env=block.env)
            block.mark()
            return True
        return False

    @staticmethod
    def key_else(block: Block):
        if len(block.header) != 2:
            raise SyntaxError("Invalid Syntax")
        if not Keywords.is_valid(["if", "elseif"], block):
            raise SyntaxError("There must be an if or elseif before else")
        if Keywords.has_ran(["if", "elseif"], block):
            return False

        for line in block.body:
            Depopulate.evaluate(Depopulate().all(line, env=block.env), env=block.env)
            block.mark()
        return True

    @staticmethod
    def is_valid(t, block: Block):
        if not isinstance(block.previous, Block):
            return False
        if block.previous.header[0] in t:
            return True
        return False

    @staticmethod
    def has_ran(t, block: Block) -> bool:
        current = block.previous
        while isinstance(current, Block) and current.header[0] in t:
            if current.ran:
                return True

            # Stop traversing
            if current.header[0] == "if":
                break

            current = current.previous

        return False