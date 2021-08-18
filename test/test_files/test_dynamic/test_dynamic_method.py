class MyClass:
    def func_1(self):
        return "1"

def func_2(func):
    return func()


def main():
    a=func_2(MyClass().func_1)
    print(a)

if __name__ == '__main__':
  main()
