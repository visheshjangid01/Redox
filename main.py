from Utils import Depopulate, Splitter
print("------------- Redox --------------")
# print(Splitter().raw("a"))
while True:
    user = input(">>> ")
    Depopulate.evaluate(Splitter().raw(user))
    if user == "exit":
        break