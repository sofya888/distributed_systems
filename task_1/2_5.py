import threading
import time
import random

# === Параметры трассы ===
finish_line = 100
obstacle_positions = [30, 60, 80]   # при пересечении — стоп 0.5с
boost_positions    = [20, 50, 70]   # при пересечении — буст x2 на 2 секунды

# === Команды и очки ===
teams = {
    "красные": ["🚗 Красная-1", "🚗 Красная-2"],
    "синие":   ["🚙 Синяя-1",   "🚙 Синяя-2"],
}
points_system = [10, 8, 6, 4, 2]  # очки за 1–5 места
team_scores = {"красные": 0, "синие": 0}
name_to_team = {name: team for team, names in teams.items() for name in names}

# === Синхронизация/результаты ===
print_lock = threading.Lock()
results_lock = threading.Lock()
results = []  # порядок финиша (имена машин)

class RacingCar:
    def __init__(self, name, speed, team):
        self.name = name
        self.base_speed = speed
        self.team = team
        self.position = 0.0
        self.boost_until = 0.0           # время (epoch), пока действует буст
        self.obstacles_hit = set()        # какие препятствия уже «сработали»
        self.boosts_used = set()          # какие бусты уже «подобраны»

    def race(self, finish_line, results_list):
        last_pos = self.position
        while self.position < finish_line:
            # --- движение за тик ---
            # действует ли сейчас буст
            now = time.time()
            boosting = now < self.boost_until
            speed_factor = 2.0 if boosting else 1.0

            move = self.base_speed * random.uniform(0.8, 1.2) * speed_factor
            self.position += move

            # --- события трассы (пересечение позиций) ---
            # препятствия
            for pos in obstacle_positions:
                if pos not in self.obstacles_hit and last_pos < pos <= self.position:
                    self.obstacles_hit.add(pos)
                    with print_lock:
                        print(f"{self.name}: ⚠️ столкнулась с препятствием на {pos}м — пауза 0.5с")
                    time.sleep(0.5)

            # ускорения
            for pos in boost_positions:
                if pos not in self.boosts_used and last_pos < pos <= self.position:
                    self.boosts_used.add(pos)
                    # буст начинает действовать с этого момента на 2 секунды
                    self.boost_until = max(self.boost_until, time.time() + 2.0)
                    with print_lock:
                        print(f"{self.name}: 🚀 ускорение на 2с у {pos}м!")

            # --- вывод прогресса ---
            with print_lock:
                bar = "█" * int(self.position // 10)
                tag = " (BOOST)" if boosting else ""
                print(f"{self.name}: {bar:10} {self.position:5.0f}м{tag}")

            last_pos = self.position
            time.sleep(0.2)

        # финиш
        with results_lock:
            results_list.append(self.name)
        with print_lock:
            print(f"🏁 {self.name} финишировал!")

def main():
    # создаём машинки (имена привязаны к командам выше)
    cars = [
        RacingCar("🚗 Красная-1", 15, "красные"),
        RacingCar("🚗 Красная-2", 14, "красные"),
        RacingCar("🚙 Синяя-1",   16, "синие"),
        RacingCar("🚙 Синяя-2",   13, "синие"),
    ]

    print("🏁 ГОНКА НАЧИНАЕТСЯ!")
    print("=" * 60)

    threads = []
    for car in cars:
        t = threading.Thread(target=car.race, args=(finish_line, results), name=car.name)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("=" * 60)
    print("🏆 Индивидуальные результаты:")
    for i, car_name in enumerate(results, 1):
        pts = points_system[i-1] if i-1 < len(points_system) else 0
        team = name_to_team.get(car_name, "?")
        team_scores[team] += pts
        print(f"{i}. {car_name} — +{pts} очков ({team})")

    print("\n📊 Командный зачёт:")
    for team, score in team_scores.items():
        print(f"Команда {team}: {score} очков")

    # победитель/ничья
    red, blue = team_scores["красные"], team_scores["синие"]
    if red > blue:
        print("\n🥇 Победа команды КРАСНЫЕ!")
    elif blue > red:
        print("\n🥇 Победа команды СИНИЕ!")
    else:
        print("\n🤝 Ничья!")

if __name__ == "__main__":
    main()
