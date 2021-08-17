class A:
   def func():
       pass

class B:
    def func():
        pass 

class C(B, A):
   pass

a = A()
b = B()
a.func()
b.func()
