# test.py
import foo

def test():
  print("I am in test.py")
  foo.test()
  def pp():
      print("pp")
  pp()

if __name__ == '__main__':
  test()
