class MyClass:
    def func_a(self):
        print("nested func a")
        def func_b():
            print("nested func b")
            def func_c():
                print("nested func c")
            func_c()

        func_b()


def func_d():
    def func_e():
        print("nested func e")
    func_e()

def main():
    a = MyClass()
    a.func_a()
    func_d()


if __name__ == "__main__":
    main()

