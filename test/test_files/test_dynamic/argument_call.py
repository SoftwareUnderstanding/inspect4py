class MyClass:
    def func_b(self):
        return 3

    def func_a(self):
         print(func_b())



def func_1():
    print(func_2())
    return 1

def func_2():
    return 2

print(func_1())
MyClass().func_a()
