#!/usr/bin/env python3
import asyncio
from homework_broker import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
