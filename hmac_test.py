import hmac
import hashlib

key = input("Ключ: ").encode()
msg = input("Сообщение: ").encode()

signature = hmac.new(key, msg, hashlib.sha256).hexdigest()
print("HMAC-SHA256:", signature)
