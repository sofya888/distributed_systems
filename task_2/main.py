import threading
import time
import random

# Создание семафора с начальным значением 3
semaphore = threading.Semaphore(3)


def worker(worker_id):
    """Функция рабочего потока"""
    print(f"Работник {worker_id} ждет доступа...")

    # Захват семафора
    semaphore.acquire()

    try:
        print(f"Работник {worker_id} получил доступ!")
        # Имитация работы
        time.sleep(random.uniform(1, 3))
        print(f"Работник {worker_id} завершил работу.")
    finally:
        # Освобождение семафора
        semaphore.release()
        print(f"Работник {worker_id} освободил доступ.")


# Создание и запуск потоков
threads = []
for i in range(10):
    print(f"Создаю поток для работника {i}...")
    t = threading.Thread(target=worker, args=(i,), name=f"WorkerThread-{i}")
    threads.append(t)
    print(f"Запускаю поток {t.name}...")
    t.start()

# Ожидание завершения всех потоков
for t in threads:
    print(f"Ожидаю завершение потока {t.name}...")
    t.join()
    print(f"Поток {t.name} завершился.")

print("Все работы завершены!")
