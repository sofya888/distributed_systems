def KSA(key):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def PRGA(S):
    i = j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        yield K

def rc4(key, text):
    key = [ord(c) for c in key]
    S = KSA(key)
    keystream = PRGA(S)
    res = bytes([c ^ next(keystream) for c in text])
    return res

key = input("Ключ: ")
msg = input("Сообщение: ").encode()

encrypted = rc4(key, msg)
print("Шифр:", encrypted)

decrypted = rc4(key, encrypted)
print("Расшифровано:", decrypted.decode())
