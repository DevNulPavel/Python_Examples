#! /usr/bin/env python3

# https://tproger.ru/translations/bittorent-client-with-python/

import asyncio
import aiofile

async def main():
    async with aiofile.AIOFile("test.torrent", "rb") as f:
        text = await f.read()
        print(text)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    