#!/usr/bin/env python3
# homework_broker.py
# Async message broker with topics, priorities, TTL, and basic auth for topics.
# Protocol: newline-delimited JSON (one JSON object per line).
# Each response is a JSON object with at least {"status": "success"|"error", ...}

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple, Set


PRIORITY_ORDER = {"high": 0, "normal": 1, "low": 2}


def utcnow():
    return datetime.now(tz=timezone.utc)


class _NLJSONProtocol:
    """Small helpers for newline-delimited JSON messages."""

    @staticmethod
    def encode(obj: Dict[str, Any]) -> bytes:
        return (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")

    @staticmethod
    def decode_line(data: bytes) -> Dict[str, Any]:
        return json.loads(data.decode("utf-8").strip())


class HomeworkBroker:
    """
    Асинхронный брокер сообщений на asyncio Streams.

    Возможности:
    - Публикация/подписка по топикам
    - list_topics / queue_length / clear_topic
    - Приоритеты сообщений: high, normal, low
    - TTL для сообщений (секунды)
    - Простейшая авторизация топиков (пароли при публикации/подписке)

    Формат сообщения от клиента (JSON per line):
    {
      "action": "publish" | "subscribe" | "unsubscribe" | "list_topics" |
                "queue_length" | "clear_topic",
      ... прочие поля ...
    }
    """

    def __init__(self) -> None:
        # topic -> asyncio.PriorityQueue of items
        # item: (priority_int, created_ts, sequence_id, payload_dict)
        self.queues: Dict[str, asyncio.PriorityQueue] = {}
        # topic -> set of writers subscribed
        self.subscribers: Dict[str, Set[asyncio.StreamWriter]] = {}
        # topic -> password (optional)
        self.topic_passwords: Dict[str, str] = {}

        # strictly increasing sequence for queue ordering
        self._seq = 0
        # protect small critical sections
        self._lock = asyncio.Lock()

    # ---------------- Core stream handling ----------------

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info("peername")
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                await self.process_message(line, writer)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            # Don't crash the server for one client; log to stderr
            err = {"status": "error", "message": f"Server exception: {e.__class__.__name__}"}
            await self.send_response(err, writer)
        finally:
            # remove writer from all subscribers sets
            await self._cleanup_writer(writer)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _cleanup_writer(self, writer: asyncio.StreamWriter) -> None:
        async with self._lock:
            for topic, subs in self.subscribers.items():
                subs.discard(writer)

    async def send_response(self, obj: Dict[str, Any], writer: asyncio.StreamWriter) -> None:
        writer.write(_NLJSONProtocol.encode(obj))
        await writer.drain()

    # ---------------- Message processing ----------------

    async def process_message(self, raw_line: bytes, writer: asyncio.StreamWriter) -> None:
        try:
            msg = _NLJSONProtocol.decode_line(raw_line)
        except json.JSONDecodeError:
            await self.send_response({"status": "error", "message": "Invalid JSON format"}, writer)
            return

        action = msg.get("action")
        if not action:
            await self.send_response({"status": "error", "message": "Missing 'action' field"}, writer)
            return

        # Route actions
        if action == "list_topics":
            await self.list_topics(writer)
            return

        if action == "queue_length":
            topic = msg.get("topic")
            if not topic:
                await self.send_response({"status": "error", "message": "Missing 'topic' field"}, writer)
                return
            await self.queue_length(topic, writer)
            return

        if action == "clear_topic":
            topic = msg.get("topic")
            if not topic:
                await self.send_response({"status": "error", "message": "Missing 'topic' field"}, writer)
                return
            await self.clear_topic(topic, msg.get("password"), writer)
            return

        if action == "publish":
            topic = msg.get("topic")
            payload = msg.get("message")
            if topic is None or payload is None:
                await self.send_response({"status": "error", "message": "Missing 'topic' or 'message' field"}, writer)
                return
            priority = msg.get("priority", "normal")
            ttl = msg.get("ttl")  # seconds
            password = msg.get("password")
            await self.publish(topic, payload, priority=priority, ttl=ttl, password=password, writer=writer)
            return

        if action == "subscribe":
            topic = msg.get("topic")
            if not topic:
                await self.send_response({"status": "error", "message": "Missing 'topic' field"}, writer)
                return
            password = msg.get("password")
            await self.subscribe(topic, writer, password=password)
            return

        if action == "unsubscribe":
            topic = msg.get("topic")
            if not topic:
                await self.send_response({"status": "error", "message": "Missing 'topic' field"}, writer)
                return
            await self.unsubscribe(topic, writer)
            return

        await self.send_response({"status": "error", "message": f"Unknown action '{action}'"}, writer)

    # ---------------- Topic utilities ----------------

    async def list_topics(self, writer: asyncio.StreamWriter) -> None:
        async with self._lock:
            topics = sorted(self.queues.keys())
        await self.send_response({"status": "success", "topics": topics}, writer)

    async def queue_length(self, topic: str, writer: asyncio.StreamWriter) -> None:
        async with self._lock:
            q = self.queues.get(topic)
        if q is None:
            await self.send_response({"status": "error", "message": f"Topic '{topic}' does not exist"}, writer)
            return
        await self._purge_expired(topic)
        size = q.qsize()
        await self.send_response({"status": "success", "topic": topic, "messages": size}, writer)

    async def clear_topic(self, topic: str, password: Optional[str], writer: asyncio.StreamWriter) -> None:
        async with self._lock:
            q = self.queues.get(topic)
            required = self.topic_passwords.get(topic)
        if q is None:
            await self.send_response({"status": "error", "message": f"Topic '{topic}' does not exist"}, writer)
            return
        if required is not None and password != required:
            await self.send_response({"status": "error", "message": "Forbidden: wrong password"}, writer)
            return
        # Drain queue
        try:
            while True:
                q.get_nowait()
        except asyncio.QueueEmpty:
            pass
        await self.send_response({"status": "success", "topic": topic, "cleared": True}, writer)

    # ---------------- Pub/Sub ----------------

    async def publish(
        self,
        topic: str,
        payload: Any,
        priority: str = "normal",
        ttl: Optional[int] = None,
        password: Optional[str] = None,
        writer: Optional[asyncio.StreamWriter] = None,
    ) -> None:
        prio = PRIORITY_ORDER.get(str(priority).lower())
        if prio is None:
            await self.send_response({"status": "error", "message": "Invalid 'priority' (use high|normal|low)"}, writer)
            return
        expires_at: Optional[datetime] = None
        if ttl is not None:
            try:
                ttl_int = int(ttl)
                if ttl_int > 0:
                    expires_at = utcnow() + timedelta(seconds=ttl_int)
            except Exception:
                await self.send_response({"status": "error", "message": "Invalid 'ttl' (seconds expected)"}, writer)
                return

        async with self._lock:
            q = self.queues.get(topic)
            if q is None:
                # create new topic on first publish; store password if provided
                q = asyncio.PriorityQueue()
                self.queues[topic] = q
                if password:
                    self.topic_passwords[topic] = password
            required = self.topic_passwords.get(topic)

            # If topic has a password, require it for publishing too.
            if required is not None and password != required:
                await self.send_response({"status": "error", "message": "Forbidden: wrong password"}, writer)
                return

            self._seq += 1
            item = (prio, utcnow().timestamp(), self._seq, {"data": payload, "expires_at": expires_at.isoformat() if expires_at else None})
            await q.put(item)

            # Copy subscribers to avoid holding the lock while IO
            subs = list(self.subscribers.get(topic, set()))

        # Push to subscribers
        if subs:
            message = {
                "type": "message",
                "topic": topic,
                "payload": payload,
                "priority": ["high", "normal", "low"][prio],
            }
            if expires_at:
                message["expires_at"] = expires_at.isoformat()
            data = _NLJSONProtocol.encode(message)
            for w in subs:
                try:
                    w.write(data)
                except Exception:
                    # ignore broken connections here; cleanup will happen later
                    pass
            # drain concurrently
            await asyncio.gather(*(w.drain() for w in subs), return_exceptions=True)

        await self.send_response({"status": "success", "topic": topic}, writer)

    async def subscribe(self, topic: str, writer: asyncio.StreamWriter, password: Optional[str] = None) -> None:
        async with self._lock:
            # create topic lazily on subscribe too (public topic)
            if topic not in self.queues:
                self.queues[topic] = asyncio.PriorityQueue()
            required = self.topic_passwords.get(topic)
            if required is not None and password != required:
                await self.send_response({"status": "error", "message": "Forbidden: wrong password"}, writer)
                return
            self.subscribers.setdefault(topic, set()).add(writer)
        await self.send_response({"status": "success", "topic": topic, "subscribed": True}, writer)

    async def unsubscribe(self, topic: str, writer: asyncio.StreamWriter) -> None:
        async with self._lock:
            subs = self.subscribers.get(topic)
            if subs:
                subs.discard(writer)
        await self.send_response({"status": "success", "topic": topic, "unsubscribed": True}, writer)

    # ---------------- Expiration helpers ----------------

    async def _purge_expired(self, topic: str) -> None:
        """Remove expired items from a topic queue (non-blocking, approximate)."""
        async with self._lock:
            q = self.queues.get(topic)
            if q is None or q.empty():
                return
            tmp: list = []
            try:
                while True:
                    item = q.get_nowait()
                    tmp.append(item)
            except asyncio.QueueEmpty:
                pass

            now = utcnow()
            # Reinsert only non-expired
            for prio, ts, seq, payload in tmp:
                exp = payload.get("expires_at")
                if exp:
                    try:
                        if datetime.fromisoformat(exp) <= now:
                            continue  # drop expired
                    except Exception:
                        pass
                q.put_nowait((prio, ts, seq, payload))


async def main(host: str = "127.0.0.1", port: int = 8888):
    broker = HomeworkBroker()
    server = await asyncio.start_server(broker.handle_client, host, port)
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Server listening on {addr}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
