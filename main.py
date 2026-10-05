from utils.depopulate import Depopulate
user = input("Filepath: ")
if not user:
    print("------------- Redox --------------")
    while True:
        user = input(">>> ")
        if user == "exit":
            break
        out = Depopulate.evaluate(Depopulate().all(user))
        if out or out == False:
            print(out)
else:
    def cleaner(line):
        if line.endswith('\n'):
            line = line[:-1]
        return line

    with open(user) as f:
        content = f.readlines()

    content = list(map(cleaner, content))
    Depopulate().line(content)