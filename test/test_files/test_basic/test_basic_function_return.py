import sys

variable_a=1

def foo(arg1, arg2):
    print("Hello %s", arg1)
    return arg2

def foo2(arg1, arg2):
    print("Hello %s", arg1)
    return {'name': arg1}

def foo3(arg1, arg2):
    print("Hello %s", arg1)
    return str(arg2)

def foo4(arg1, arg2):
    a=[1,2,3]
    return a

def foo5(arg1, arg2):
    a={}
    a['name']= arg1
    return a

def foo6(arg1, arg2):
    return [0,2,3]
