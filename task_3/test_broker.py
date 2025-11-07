# tests/test_broker.py
import asyncio
import json
import unittest
from homework_broker import HomeworkBroker, _NLJSONProtocol

class FakeWriter:
    def __init__(self):
        self.buffer = bytearray()
        self.closed = False

    def write(self, data: bytes):
        self.buffer.extend(data)

    async def drain(self):
        await asyncio.sleep(0)

    def getvalue(self):
        return bytes(self.buffer)

    def reset(self):
        self.buffer.clear()

    def get_extra_info(self, name):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        pass

class BrokerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.broker = HomeworkBroker()
        self.w1 = FakeWriter()
        self.w2 = FakeWriter()

    async def _read_jsons(self, writer: FakeWriter):
        data = writer.getvalue().decode("utf-8").strip().splitlines()
        return [json.loads(x) for x in data if x.strip()]

    async def test_list_topics_initially_empty(self):
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"list_topics"}), self.w1)
        res = await self._read_jsons(self.w1)
        self.assertEqual(res[-1]["status"], "success")
        self.assertEqual(res[-1]["topics"], [])

    async def test_publish_subscribe(self):
        # subscribe
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"subscribe","topic":"news"}), self.w1)
        # publish
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"publish","topic":"news","message":"Hello"}), self.w2)
        msgs = await self._read_jsons(self.w1)
        # last push should be a server 'message' to subscriber
        self.assertTrue(any(m.get("type")=="message" and m.get("payload")=="Hello" for m in msgs))

    async def test_multiple_clients_receive(self):
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"subscribe","topic":"t"}), self.w1)
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"subscribe","topic":"t"}), self.w2)
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"publish","topic":"t","message":"X"}), self.w1)
        r1 = await self._read_jsons(self.w1)
        r2 = await self._read_jsons(self.w2)
        self.assertTrue(any(m.get("type")=="message" and m.get("payload")=="X" for m in r1))
        self.assertTrue(any(m.get("type")=="message" and m.get("payload")=="X" for m in r2))

    async def test_error_handling_invalid_json(self):
        await self.broker.process_message(b'{"action": "publish"', self.w1)  # broken JSON
        res = await self._read_jsons(self.w1)
        self.assertEqual(res[-1]["status"], "error")

    async def test_queue_length_and_clear(self):
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"publish","topic":"q","message":"1"}), self.w1)
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"queue_length","topic":"q"}), self.w1)
        res1 = await self._read_jsons(self.w1)
        self.assertEqual(res1[-1]["messages"], 1)
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"clear_topic","topic":"q"}), self.w1)
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"queue_length","topic":"q"}), self.w1)
        res2 = await self._read_jsons(self.w1)
        self.assertEqual(res2[-1]["messages"], 0)

    async def test_ttl_expiration(self):
        # publish with short TTL
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"publish","topic":"ttl","message":"tmp","ttl":1}), self.w1)
        await asyncio.sleep(1.2)
        await self.broker.process_message(_NLJSONProtocol.encode({"action":"queue_length","topic":"ttl"}), self.w1)
        res = await self._read_jsons(self.w1)
        self.assertEqual(res[-1]["messages"], 0)


if __name__ == "__main__":
    unittest.main()
