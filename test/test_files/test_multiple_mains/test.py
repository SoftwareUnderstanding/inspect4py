# test.py
import bar  # use an absolute import
import foo
import lalo 
def test():
  print("I am in test.py")
  bar.test()
  foo.test()
  lalo.lalo()
  def pp():
      print("pp")
  pp()

if __name__ == '__main__':
  test()
