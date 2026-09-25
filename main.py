from utils.depopulate import Depopulate
print("------------- Redox --------------")
# print(Splitter().raw("a"))
while True:
    user = input(">>> ")
    out = Depopulate.evaluate(Depopulate().all(user))
    if out or out == False:
        print(out)
    if user == "exit":
        break