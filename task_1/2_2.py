import threading
import time
import random

# --- Константы по заданию ---
MAX_BALANCE = 500
COMMISSION = 1

# Общая история всех операций (помимо локальной истории счета)
operations_history = []
history_lock = threading.Lock()  # отдельная блокировка для истории


class BankAccount:
    def __init__(self):
        self.balance = 100
        self.max_balance = MAX_BALANCE
        self.lock = threading.Lock()  # защищает баланс
        self.history = []             # локальная история именно этого счета

    def _log(self, message: str):
        """Добавить запись в историю (общую и локальную)"""
        stamp = time.strftime("%H:%M:%S")
        who = threading.current_thread().name
        entry = f"{stamp} [{who}] {message} (баланс: {self.balance})"
        # пишем историю под отдельным локом, чтобы не мешать другим
        with history_lock:
            operations_history.append(entry)
            self.history.append(entry)

    def deposit(self, amount: int):
        """Пополнение: не превышаем max_balance"""
        with self.lock:
            if self.balance >= self.max_balance:
                self._log(f"Пополнение {amount} ОТКЛОНЕНО — достигнут лимит {self.max_balance}")
                return 0

            # сколько реально можно зачислить до лимита
            can_add = min(amount, self.max_balance - self.balance)
            self.balance += can_add
            if can_add < amount:
                self._log(f"Пополнение запрошено {amount}, зачислено {can_add} (упёрлись в лимит {self.max_balance})")
            else:
                self._log(f"Пополнение {amount}")
            return can_add

    def withdraw(self, amount: int):
        """Снятие: учитываем комиссию"""
        total = amount + COMMISSION
        with self.lock:
            if self.balance >= total:
                self.balance -= total
                self._log(f"Снятие {amount} + комиссия {COMMISSION}")
                return amount
            else:
                self._log(f"Снятие {amount} ОТКЛОНЕНО — требуется {total}, доступно {self.balance}")
                return 0


# --- Рабочие функции потоков ---
def depositor(acc: BankAccount, times: int):
    for _ in range(times):
        amt = random.randint(10, 60)
        acc.deposit(amt)
        time.sleep(random.uniform(0.05, 0.2))


def withdrawer(acc: BankAccount, times: int):
    for _ in range(times):
        amt = random.randint(10, 50)
        acc.withdraw(amt)
        time.sleep(random.uniform(0.05, 0.2))


# --- Тест: 2 потока пополнения и 2 потока снятия ---
if __name__ == "__main__":
    account = BankAccount()

    threads = [
        threading.Thread(target=depositor,  name="Пополнение-1", args=(account, 5)),
        threading.Thread(target=depositor,  name="Пополнение-2", args=(account, 5)),
        threading.Thread(target=withdrawer, name="Снятие-1",     args=(account, 7)),
        threading.Thread(target=withdrawer, name="Снятие-2",     args=(account, 7)),
    ]

    for t in threads: t.start()
    for t in threads: t.join()

    print("\n=== Итог ===")
    print(f"Текущий баланс: {account.balance}")

    print("\n=== История операций (по времени) ===")
    for rec in operations_history:
        print(rec)
