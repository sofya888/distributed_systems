from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Гарантированно правильный ключ 16 байт (AES-128)
key = b"1234567890ABCDEF"  
print("Длина ключа:", len(key))

cipher = AES.new(key, AES.MODE_ECB)

text = input("Введите текст: ").encode()

encrypted = cipher.encrypt(pad(text, 16))
print("Зашифровано:", encrypted)

cipher2 = AES.new(key, AES.MODE_ECB)
decrypted = unpad(cipher2.decrypt(encrypted), 16)
print("Расшифровано:", decrypted.decode())
