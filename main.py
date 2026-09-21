from pathlib import Path

base = Path("./project")

user = input("File name: ")
mutable_vars  = {}
immutable_vars = {}

with open(base / user + ".rx") as f:
    code = f.readlines()

# strips away newline chars
code = [line.rstrip('\n') for line in code]

for line in code:
    comps = line.split()
    if len(comps) == 3:
        # Simple Variable Assignment
        if comps[1] == "->" or comps[1] == "=>":
            if comps[2] not in immutable_vars.keys():
                if comps[1].startswith("-"):
                    mutable_vars[comps[2]] = comps[0]
                else:
                    immutable_vars[comps[2]] = comps[0]
            else:
                raise ValueError("Cannot update an immutable variable")

            continue
