import random

p = 23       # простое
g = 5        # генератор

# секреты сторон
a = random.randint(1, p-1)
b = random.randint(1, p-1)

A = pow(g, a, p)
B = pow(g, b, p)

K1 = pow(B, a, p)
K2 = pow(A, b, p)

print("Алиса → Боб:", A)
print("Боб → Алиса:", B)

print("Общий ключ Алисы:", K1)
print("Общий ключ Боба: ", K2)
