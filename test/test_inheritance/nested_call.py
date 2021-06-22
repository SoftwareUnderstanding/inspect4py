class MyClass:
    def func(self):
        def nested():
            pass

        nested()

def test():
    a = MyClass()
    a.func()
