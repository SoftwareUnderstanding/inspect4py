from .test_classes import *
from .test_functions import *

class MyClass_D:
    def __init__(self):
        print("Class D")
        funct_C()
        funct_D()
        MyClass_E()

class MyClass_E:
    def __init__(self):
        print("Class E")
        MyClass_B()

def funct_D():
    print("Function D")
    a=MyClass_A()
    MyClass_E()
    funct_A()

MyClass_A()
b1=MyClass_B()
d= MyClass_D()
funct_A()
funct_D()
MyClass_C()
c=funct_D()
