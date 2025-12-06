from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Генерация ключей
key = RSA.generate(2048)
private_key = key
public_key = key.publickey()

encryptor = PKCS1_OAEP.new(public_key)
decryptor = PKCS1_OAEP.new(private_key)

msg = input("Введите сообщение: ").encode()

ciphertext = encryptor.encrypt(msg)
print("Зашифровано:", ciphertext)

plaintext = decryptor.decrypt(ciphertext)
print("Расшифровано:", plaintext.decode())
