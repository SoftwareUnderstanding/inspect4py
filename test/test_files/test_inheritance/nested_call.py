class MyClass:
    def func(self):
        def nested():
            print("nested")

        nested()

def test():
    a = MyClass()
    a.func()

test()
