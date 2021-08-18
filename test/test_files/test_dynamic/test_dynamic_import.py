import test_dynamic_func

def func_3(func):
    return func()


a=func_3(test_dynamic_func.func_1)
print(a)
