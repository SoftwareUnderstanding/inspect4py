class A:
   def func():
       pass

class B:
    def func():
        pass 

class C(B, A):
   pass

c = C()
c.func()
