import asyncio
import random
from datetime import datetime

class AsyncMessageQueue:
    def __init__(self, max_size=10):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.producers = []
        self.consumers = []
        self.is_running = False
    
    async def producer(self, name, interval=1):
        """Производитель сообщений"""
        message_id = 0
        while self.is_running:
            try:
                await asyncio.sleep(interval)
                message = f"Сообщение {message_id} от {name}"
                await asyncio.wait_for(
                    self.queue.put((message, datetime.now())),
                    timeout=0.1
                )
                print(f"📨 [{name}] Отправлено: {message}")
                message_id += 1
            except asyncio.TimeoutError:
                print(f"⚠️  [{name}] Очередь переполнена, пропускаем...")
            except Exception as e:
                print(f"❌ [{name}] Ошибка: {e}")
    
    async def consumer(self, name, process_time=2):
        """Потребитель сообщений"""
        while self.is_running:
            try:
                message, timestamp = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                await asyncio.sleep(process_time)
                delay = (datetime.now() - timestamp).total_seconds()
                print(f"✅ [{name}] Обработано: '{message}' | Задержка: {delay:.2f}с")
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ [{name}] Ошибка обработки: {e}")
    
    async def monitor(self):
        """Мониторинг очереди"""
        while self.is_running:
            size = self.queue.qsize()
            print(f"📊 Монитор: В очереди {size} сообщений")
            await asyncio.sleep(5)
    
    async def run(self, num_producers=2, num_consumers=3, duration=30):
        """Запуск системы"""
        self.is_running = True
        print("🚀 Запуск асинхронной очереди...")
        for i in range(num_producers):
            interval = random.uniform(0.5, 2.0)
            task = asyncio.create_task(self.producer(f"Producer-{i}", interval))
            self.producers.append(task)
        for i in range(num_consumers):
            process_time = random.uniform(1.0, 3.0)
            task = asyncio.create_task(self.consumer(f"Consumer-{i}", process_time))
            self.consumers.append(task)
        monitor_task = asyncio.create_task(self.monitor())
        print(f"⏰ Работаем {duration} секунд...")
        await asyncio.sleep(duration)
        await self.stop()
        await monitor_task
    
    async def stop(self):
        """Остановка системы"""
        print("🛑 Останавливаем систему...")
        self.is_running = False
        if not self.queue.empty():
            print("⏳ Завершаем обработку оставшихся сообщений...")
            await self.queue.join()
        for task in self.producers + self.consumers:
            task.cancel()
        await asyncio.gather(*self.producers, *self.consumers, return_exceptions=True)

# Дополнительные примеры для изучения
async def basic_async_examples():
    """Базовые примеры асинхронности"""
    print("\n" + "="*50)
    print("БАЗОВЫЕ ПРИМЕРЫ АСИНХРОННОСТИ")
    print("="*50)
    async def simple_task(name, seconds):
        print(f"Задача '{name}' началась")
        await asyncio.sleep(seconds)
        print(f"Задача '{name}' завершилась через {seconds}с")
        return f"Результат {name}"
    results = await asyncio.gather(
        simple_task("A", 2),
        simple_task("B", 1),
        simple_task("C", 3)
    )
    print(f"Результаты: {results}")
    # ИСПРАВЛЕНО: однажды async
    async def message_generator(count):
        for i in range(count):
            yield f"Сообщение {i}"
            await asyncio.sleep(0.5)
    print("Генератор сообщений:")
    async for message in message_generator(3):
        print(f"  Получено: {message}")
    async def limited_task(semaphore, name, duration):
        async with semaphore:
            print(f"Задача '{name}' начала работу (лимит: {semaphore._value})")
            await asyncio.sleep(duration)
            print(f"Задача '{name}' завершилась")
    semaphore = asyncio.Semaphore(2)
    tasks = [limited_task(semaphore, f"Task-{i}", random.uniform(1, 3)) for i in range(5)]
    await asyncio.gather(*tasks)

# Усовершенствованная очередь с приоритетами
class PriorityMessageQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
    async def add_message(self, message, priority=5):
        """Добавление сообщения с приоритетом (меньше = выше приоритет)"""
        await self.queue.put((priority, message))
        print(f"➕ Добавлено: {message} (приоритет: {priority})")
    async def process_messages(self, worker_name):
        """Обработка сообщений с приоритетами"""
        while True:
            try:
                priority, message = await asyncio.wait_for(self.queue.get(), timeout=2.0)
                print(f"🎯 [{worker_name}] Обрабатывается: {message} (приоритет: {priority})")
                await asyncio.sleep(1)
                self.queue.task_done()
            except asyncio.TimeoutError:
                print(f"⏰ [{worker_name}] Нет сообщений, завершаем...")
                break

async def demo_priority_queue():
    """Демонстрация очереди с приоритетами"""
    print("\n" + "="*50)
    print("ОЧЕРЕДЬ С ПРИОРИТЕТАМИ")
    print("="*50)
    pq = PriorityMessageQueue()
    messages = [
        ("Важное сообщение", 1),
        ("Обычное сообщение", 5),
        ("Срочное сообщение", 0),
        ("Низкий приоритет", 10),
    ]
    for msg, priority in messages:
        await pq.add_message(msg, priority)
    await pq.process_messages("Worker-1")

# Основная функция
async def main():
    """Главная функция с демонстрациями"""
    await basic_async_examples()
    await demo_priority_queue()
    print("\n" + "="*50)
    print("ОСНОВНАЯ СИСТЕМА ОЧЕРЕДЕЙ")
    print("="*50)
    queue_system = AsyncMessageQueue(max_size=5)
    await queue_system.run(
        num_producers=2,
        num_consumers=3, 
        duration=15  # Работаем 15 секунд для демонстрации
    )

# Утилиты для тестирования
async def stress_test():
    """Стресс-тест системы"""
    print("\n🧪 СТРЕСС-ТЕСТ СИСТЕМЫ")
    stress_queue = AsyncMessageQueue(max_size=3)
    await stress_queue.run(
        num_producers=5,
        num_consumers=2,
        duration=10
    )

if __name__ == "__main__":
    asyncio.run(main())
    # Дополнительно: запуск стресс-теста
    # asyncio.run(stress_test())
