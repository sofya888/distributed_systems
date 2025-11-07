#!/usr/bin/env python3
# client.py - Interactive asyncio client for HomeworkBroker
import asyncio
import json
from typing import Any, Dict

HOST = "127.0.0.1"
PORT = 8888

def jline(obj: Dict[str, Any]) -> bytes:
    return (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")

async def ainput(prompt: str = "") -> str:
    # run blocking input in a thread so event loop stays responsive
    return await asyncio.to_thread(input, prompt)

async def reader_task(reader: asyncio.StreamReader):
    while True:
        line = await reader.readline()
        if not line:
            print("\n[Disconnected]")
            return
        try:
            msg = json.loads(line.decode("utf-8").strip())
            if msg.get("type") == "message":
                print(f"\n[Message] topic={msg['topic']} priority={msg.get('priority')}: {msg['payload']}")
            else:
                print(f"\n[Response] {json.dumps(msg, ensure_ascii=False)}")
        except Exception as e:
            print(f"\n[Bad line] {line!r} ({e})")

def show_menu():
    print("\n=== Message Broker Client ===")
    print("1. List topics")
    print("2. Subscribe to topic")
    print("3. Publish message")
    print("4. Get message count")
    print("5. Clear topic")
    print("6. Unsubscribe from topic")
    print("7. Exit")

async def main():
    reader, writer = await asyncio.open_connection(HOST, PORT)
    print(f"Connected to {HOST}:{PORT}")
    # start background reader
    rt = asyncio.create_task(reader_task(reader))

    try:
        while True:
            show_menu()
            choice = (await ainput("Select option: ")).strip()

            if choice == "1":
                writer.write(jline({"action": "list_topics"}))
                await writer.drain()

            elif choice == "2":
                topic = (await ainput("Topic: ")).strip()
                pwd = (await ainput("Password (optional): ")).strip() or None
                msg = {"action": "subscribe", "topic": topic}
                if pwd: msg["password"] = pwd
                writer.write(jline(msg)); await writer.drain()

            elif choice == "3":
                topic = (await ainput("Topic: ")).strip()
                text = (await ainput("Message: ")).strip()
                priority = (await ainput("Priority [high|normal|low] (default normal): ")).strip() or "normal"
                ttl = (await ainput("TTL seconds (optional): ")).strip()
                pwd = (await ainput("Password (optional): ")).strip() or None
                msg = {"action": "publish", "topic": topic, "message": text, "priority": priority}
                if ttl:
                    try:
                        msg["ttl"] = int(ttl)
                    except ValueError:
                        print("TTL must be an integer; ignoring.")
                if pwd: msg["password"] = pwd
                writer.write(jline(msg)); await writer.drain()

            elif choice == "4":
                topic = (await ainput("Topic: ")).strip()
                writer.write(jline({"action": "queue_length", "topic": topic})); await writer.drain()

            elif choice == "5":
                topic = (await ainput("Topic: ")).strip()
                pwd = (await ainput("Password (optional): ")).strip() or None
                msg = {"action": "clear_topic", "topic": topic}
                if pwd: msg["password"] = pwd
                writer.write(jline(msg)); await writer.drain()

            elif choice == "6":
                topic = (await ainput("Topic: ")).strip()
                writer.write(jline({"action": "unsubscribe", "topic": topic})); await writer.drain()

            elif choice == "7":
                print("Bye!")
                break
            else:
                print("Unknown option.")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        await asyncio.sleep(0.05)
        rt.cancel()
        try:
            await rt
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
