"""
splits components of a block into raw elements/components
"""
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

def raw(line: str) -> list:
    invalid = [',']
    return splitter(line, invalid)

def bracket(line: str) -> list:
    invalid = [
        # Operators
        '=>', '->', ';'
    ]
    return splitter(line, invalid)