# Async Message Broker (Homework)

Асинхронный брокер сообщений на `asyncio` со следующими возможностями:

- Публикация/подписка по топикам
- Список топиков (`list_topics`)
- Подсчёт сообщений в топике (`queue_length`)
- Очистка топика (`clear_topic`)
- Приоритеты сообщений: `high | normal | low`
- TTL (время жизни) сообщений (в секундах)
- Простейшая авторизация топиков по паролю (опционально)

## Быстрый старт

```bash
python run_server.py
```

В другом терминале запуск клиента:

```bash
python client.py
```

## Протокол

Сообщения — **JSON по одной строке**. Ответы сервера также — JSON по одной строке.

### Запросы от клиента

```json
{"action":"list_topics"}

{"action":"queue_length", "topic":"news"}

{"action":"clear_topic", "topic":"news", "password":"secret"}

{"action":"publish", "topic":"news", "message":"Hello", "priority":"high", "ttl":60, "password":"secret"}

{"action":"subscribe", "topic":"news", "password":"secret"}

{"action":"unsubscribe", "topic":"news"}
```

### Ответы сервера (примеры)

```json
{"status":"success","topics":["news"]}
{"status":"success","topic":"news","messages":3}
{"status":"success","topic":"news","cleared":true}
{"status":"success","topic":"news"}
{"status":"success","topic":"news","subscribed":true}
{"status":"success","topic":"news","unsubscribed":true}
```

Сообщения, доставляемые подписчикам, имеют вид:

```json
{"type":"message","topic":"news","payload":"Hello","priority":"normal","expires_at":"2025-11-08T10:00:00+00:00"}
```

## Клиент

Интерактивное меню:
```
1. List topics
2. Subscribe to topic
3. Publish message
4. Get message count
5. Clear topic
6. Unsubscribe from topic
7. Exit
```

В клиенте поддерживается асинхронный вывод: входящие сообщения показываются в консоли, даже когда вы вводите команды.

## Обработка ошибок

Сервер возвращает объекты с `{"status":"error","message":"..."}` в случаях:

- Невалидный JSON
- Неизвестное действие
- Отсутствующие поля (`topic`, `message`, `action`)
- Запрос к несуществующему топику (для некоторых операций)
- Неверный пароль для защищённого топика

## Авторизация топиков

- Пароль можно задать **при первом `publish`** или хранится уже заданный в сервере.
- Для `publish`, `subscribe` и `clear_topic` требуется правильный пароль, если он задан для топика.

## Тесты

Тесты написаны на `unittest` (асинхронные, `IsolatedAsyncioTestCase`). Запуск:

```bash
python -m unittest discover -s tests -v
```

Покрываются сценарии:
- Пустой список топиков
- Публикация и доставка подписчикам
- Несколько клиентов-подписчиков
- Обработка невалидного JSON
- Подсчёт и очистка очереди
- TTL сообщений
