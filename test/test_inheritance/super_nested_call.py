class MyClass:
    def func(self):
        def f_nested():
            print("nested")
            def supernested():
                print("nested")

        f_nested()

def test():
    a = MyClass()
    a.func()


def kk():
    def pp():
        print("pp")
    pp()

if __name__ == "__main__":
    test()
