import hashlib

text = input("Введите строку: ").encode()

print("MD5:", hashlib.md5(text).hexdigest())
print("SHA1:", hashlib.sha1(text).hexdigest())
print("SHA256:", hashlib.sha256(text).hexdigest())
print("SHA512:", hashlib.sha512(text).hexdigest())
print("SHA3-256:", hashlib.sha3_256(text).hexdigest())
print("SHA3-512:", hashlib.sha3_512(text).hexdigest())
