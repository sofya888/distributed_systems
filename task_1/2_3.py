import threading
import time
import random
from queue import PriorityQueue
from itertools import count

# --- Конфиг ---
product_types = ["еда", "одежда", "электроника"]
producers_config = [
    {"name": "Фабрика-А", "type": "еда",         "count": 3},
    {"name": "Фабрика-Б", "type": "одежда",      "count": 4},
    {"name": "Фабрика-В", "type": "электроника", "count": 2},
]
priority_map = {"еда": 1, "электроника": 2, "одежда": 3}

q = PriorityQueue()
seq = count()  # глобальный монотонный счётчик для tie-break

def producer(q: PriorityQueue, name: str, product_type: str, count_items: int):
    prio = priority_map[product_type]
    for i in range(count_items):
        item = {"type": product_type, "producer": name, "idx": i}
        q.put((prio, next(seq), item))  # (приоритет, порядковый номер, данные)
        print(f"🛠️  {name} произвёл: {product_type}-{i} (prio={prio})")
        time.sleep(random.uniform(0.05, 0.2))

def consumer(q: PriorityQueue, name: str, accepts=None):
    accepts_set = set(accepts) if accepts else None
    while True:
        prio, _, item = q.get()  # берём кортеж, item может быть None (сигнал остановки)
        if item is None:
            q.task_done()
            print(f"🛑 {name}: стоп")
            break

        ptype = item["type"]
        if accepts_set is None or ptype in accepts_set:
            print(f"🛒 {name} купил: {ptype} от {item['producer']}-{item['idx']} (prio={prio})")
            time.sleep(random.uniform(0.1, 0.3))
            q.task_done()
        else:
            # не мой тип — возвращаю обратно (с новым seq)
            q.task_done()
            q.put((prio, next(seq), item))
            time.sleep(0.05)

if __name__ == "__main__":
    # производители
    prod_threads = [
        threading.Thread(target=producer,
                         args=(q, cfg["name"], cfg["type"], cfg["count"]),
                         name=f"PROD-{cfg['name']}")
        for cfg in producers_config
    ]
    # потребители
    consumers_config = [
        {"name": "Магазин-Все",   "accepts": None},
        {"name": "ЭлектроМаркет", "accepts": {"электроника"}},
        {"name": "Фудкорт",       "accepts": {"еда"}},
    ]
    cons_threads = [
        threading.Thread(target=consumer,
                         args=(q, c["name"], c["accepts"]),
                         name=f"CONS-{c['name']}")
        for c in consumers_config
    ]

    print("🚀 Стартуем производителей и потребителей...")
    for t in prod_threads: t.start()
    for t in cons_threads: t.start()

    for t in prod_threads: t.join()  # производители закончили класть товары
    q.join()                         # все реальные товары обработаны

    # Посылаем стоп-сентинелы (столько, сколько потребителей)
    for _ in cons_threads:
        q.put((float('inf'), next(seq), None))  # самый низкий приоритет + уникальный seq

    for t in cons_threads: t.join()
    print("🎉 Все товары обработаны, все потоки завершены.")
