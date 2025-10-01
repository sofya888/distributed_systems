import threading
import time

# === Переменные из задания ===
colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m"]  # красный, зелёный, жёлтый, синий
reset_color = "\033[0m"

start_number = 5
letters = "EDCBA"  # обратный порядок

# === Функции с параметрами color и thread_id ===
def print_numbers(color, thread_id, start):
    for i in range(start, 0, -1):  # 5,4,3,2,1
        print(f"{color}Поток-{thread_id}: число {i}{reset_color}")
        time.sleep(1)
    print(f"{color}Поток-{thread_id} завершен!{reset_color}")

def print_letters(color, thread_id, seq):
    for letter in seq:  # 'E','D','C','B','A'
        print(f"{color}Поток-{thread_id}: буква {letter}{reset_color}")
        time.sleep(1)
    print(f"{color}Поток-{thread_id} завершен!{reset_color}")

# === Создаём 4 потока с разными цветами ===
threads = [
    threading.Thread(target=print_numbers, args=(colors[0], 1, start_number)),
    threading.Thread(target=print_letters, args=(colors[1], 2, letters)),
    threading.Thread(target=print_numbers, args=(colors[2], 3, start_number)),
    threading.Thread(target=print_letters, args=(colors[3], 4, letters)),
]

# === Запуск всех потоков одновременно ===
for t in threads:
    t.start()

# === Ожидание завершения ===
for t in threads:
    t.join()

