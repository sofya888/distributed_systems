import threading
import time
import random

# === Параметры по заданию ===
bar_width = 20            # ширина прогресс-бара
update_interval = 0.2     # раз в сколько секунд обновлять бар
max_simultaneous_downloads = 3

download_semaphore = threading.Semaphore(max_simultaneous_downloads)

# === Общие штуки для аккуратного вывода и счётчика активных скачиваний ===
print_lock = threading.Lock()
active_lock = threading.Lock()
active_downloads = 0      # сколько сейчас качается одновременно


def draw_progress(filename, percent, active_now, total_files):
    """Рисуем прогресс-бар одной строкой (потокобезопасно)."""
    filled = int(percent / 100 * bar_width)
    empty = bar_width - filled
    bar = "[" + "#" * filled + "_" * empty + "]"
    with print_lock:
        # filename выровняем, чтобы столбцы были аккуратнее
        print(f"{filename:12} {bar} {percent:5.1f}% | Скачивается {active_now}/{total_files}", flush=True)


def download_file(filename, size, total_files):
    """
    Имитация загрузки файла с прогресс-баром.
    Ограничиваем число параллельных скачиваний семафором.
    """
    global active_downloads

    # Захватываем «право качать»: не больше N одновременно
    download_semaphore.acquire()
    with active_lock:
        active_downloads += 1
        current_active = active_downloads

    # Случайная длительность "скачивания"
    download_time = random.uniform(1, 3)

    start = time.time()
    end = start + download_time

    # Первичное сообщение о старте
    draw_progress(filename, 0.0, current_active, total_files)

    try:
        # Обновляем бар каждые update_interval
        while True:
            now = time.time()
            if now >= end:
                break
            percent = min(100.0, (now - start) / download_time * 100.0)
            # читаем актуальное число активных
            with active_lock:
                current_active = active_downloads
            draw_progress(filename, percent, current_active, total_files)
            time.sleep(update_interval)

        # Финальный кадр на 100%
        with active_lock:
            current_active = active_downloads
        draw_progress(filename, 100.0, current_active, total_files)

        # Сообщение о завершении
        with print_lock:
            print(f"✅ Завершена загрузка: {filename} ({download_time:.1f} сек)", flush=True)

    finally:
        # Освобождаем «право качать»
        with active_lock:
            active_downloads -= 1
        download_semaphore.release()


# === Пример использования ===
if __name__ == "__main__":
    files = [
        ("document.pdf", 2.5),
        ("image.jpg",    1.8),
        ("video.mp4",    3.0),
        ("music.mp3",    2.2),
        ("archive.zip",  2.7),
    ]
    total = len(files)

    print("🚀 Начинаем параллельную загрузку с лимитом по одновременным скачиваниям...")
    start_time = time.time()

    threads = []
    for filename, size in files:
        t = threading.Thread(target=download_file, args=(filename, size, total), name=f"DL-{filename}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_time = time.time() - start_time
    print(f"⏱️  Все загрузки завершены за {total_time:.1f} сек")
