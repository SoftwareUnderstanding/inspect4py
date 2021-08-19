import test_dynamic_func

class MyClass:
    def func_3(self, func):
        return func()

a=MyClass()
a.func_3(test_dynamic_func.func_1)
