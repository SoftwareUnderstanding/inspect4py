import cryptops

class Crypto:
    def __init__(self, key):
        self.key = key

    def apply(self, msg, func):
        return func(self.key, msg)

def test():
    crp = Crypto("secretkey")
    encrypted = crp.apply("hello world",cryptops.encrypt)
    decrypted = crp.apply(encrypted, cryptops.decrypt)
