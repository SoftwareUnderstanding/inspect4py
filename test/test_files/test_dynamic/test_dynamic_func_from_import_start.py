from test_dynamic_func import *

def func_3(func):
    return func()

def main():
    a=func_3(func_1)
    print(a)

if __name__ == '__main__':
  main()
