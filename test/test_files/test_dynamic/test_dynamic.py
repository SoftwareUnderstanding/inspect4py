def func_1():
    return "1"

def func_2(func):
    return func()


a=func_2(func_1)
print(a)
