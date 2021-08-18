import test_dynamic_func as td

def func_3(func):
    return func()


a=func_3(td.func_1)
print(a)
