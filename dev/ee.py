class C:
    def __init__(self, **kargs):
        for i in kargs:
            self.__setattr__(i, kargs[i])


x = C(name="hola", value="value")
print(x)
print(x.name)