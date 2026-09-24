from Utils import Depopulate, Splitter
print("------------- Redox --------------")
# print(Splitter().raw("a"))
while True:
    user = input(">>> ")
    Depopulate.evaluate(Depopulate().all(user))
    if user == "exit":
        break