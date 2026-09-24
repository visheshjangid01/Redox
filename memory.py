class Env:
    mutable = {}
    immutable = {}
    functions = {}

    def __init__(self, parent=None):
        self.parent = parent

    def set_var(self, name, value, is_mutable=True):
        current = self
        while not current.find_var(name) and current.parent is not None:
            current = current.parent
        if is_mutable:
            if name in current.immutable:
                raise ValueError("Variable already defined!")
            current.mutable[name] = value
        else:
            if name in current.immutable:
                raise ValueError("Variable already defined!")
            if name in current.mutable:
                current.mutable.pop(name)
            current.immutable[name] = value


    def find_var(self, name):
        if name in self.immutable:
            return "immutable"
        elif name in self.mutable:
            return "mutable"
        else:
            return None

    def get_var(self, name):
        if name in self.immutable:
            return self.immutable[name]
        elif name in self.mutable:
            return self.mutable[name]
        else:
            if not self.parent:
                raise ValueError("Variable not defined!")
            else:
                return self.parent.get_var(name)
                # return id(self.parent)

    def set_func(self, name, line_no):
        if not self.get_var(name):
            self.functions[name] = line_no
        else:
            raise KeyError("Function already defined!")

    def get_func(self, name):
        if name in self.functions:
            return self.functions[name]
        else:
            if not self.parent:
                return None
            else:
                return self.parent.get_func(name)

glob = Env()
