from utils.depopulate import Depopulate
print("------------- Redox --------------")
# print(Splitter().raw("a"))

while True:
    user = input(">>> ")
    if user == "exit":
        break
    out = Depopulate.evaluate(Depopulate().all(user))
    if out or out == False:
        print(out)