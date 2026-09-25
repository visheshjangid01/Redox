from utils.reserved import Operators

class Tools:
    """
    Methods:
    - Order: gives correct order of operators to be solved
    - is_valid_string: Checks if it is a valid string component
    """
    @staticmethod
    def order(comps):
        temp = comps.copy()
        out = []
        for level, ops in Operators().all.items():
            for item in list(temp):
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

class Splitter:
    """
    splits components of a block into raw elements/components
    """
    @staticmethod
    def split(line: str, invalid: list) -> list:
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
                char_count += 1
                if quote is None:
                    quote = char
                elif char == quote:
                    quote = None
            p2 += 1

        if char_count > 0:
            comps.append(line[p1:])

        return comps
