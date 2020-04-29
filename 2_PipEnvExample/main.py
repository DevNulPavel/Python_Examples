#! /usr/bin/env python3

import asyncio
import aiohttp


async def performRequestForSession(session: aiohttp.ClientSession):
    getParams = {
        "key1": "value1", 
        "key2": "value2"
    }
    async with session.get("http://httpbin.org/get", params=getParams) as response:
        response: aiohttp.ClientResponse

        print(response.url)
        print(response.status)
        #return await response.text()

        chunkSize = 128
        with open("result.html", "wb") as fd:
            while True:
                chunk = await response.content.read(chunkSize)
                if not chunk:
                    break
                fd.write(chunk)

        return "Success"


async def main():
    async with aiohttp.ClientSession() as session:
        response = await performRequestForSession(session)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())