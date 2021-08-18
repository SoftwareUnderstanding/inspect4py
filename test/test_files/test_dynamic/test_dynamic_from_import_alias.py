from test_dynamic_func import func_1 as rosa

def func_3(func):
    return func()


a=func_3(rosa)
print(a)
