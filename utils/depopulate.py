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

    def all(self, line, invalid=None, env=glob, is_block=False) -> list:

        if invalid is None:
            invalid = self.invalids
        comps=[]
        if isinstance(line, str):
            comps = Splitter().split(line)

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

    @staticmethod
    def line(lines: list):
        result = []
        env = Env(glob)
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
                    block_env = Env(block.env)
                else:
                    current_prev = global_prev
                    block_env = Env(env)

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

class Keywords:
    @staticmethod
    def key_if(comps):
        if comps.index("if") != 0:
            raise SyntaxError("Invalid Syntax")
        if comps.index(":") != len(comps) - 1:
            raise SyntaxError("Invalid Syntax")
        invalid = ["if", "else", "elseif", "func"] + Operators.assignment
        if not Depopulate().all(comps[1:-1], invalid):
            pass

# Depopulate.line(["  Hi", "  Hello  "])