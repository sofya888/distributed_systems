from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

key = b"12345678"      # ключ строго 8 байт
cipher = DES.new(key, DES.MODE_ECB)

text = input("Введите текст: ").encode()

encrypted = cipher.encrypt(pad(text, 8))
print("Зашифровано:", encrypted)

cipher2 = DES.new(key, DES.MODE_ECB)
decrypted = unpad(cipher2.decrypt(encrypted), 8)
print("Расшифровано:", decrypted.decode())
