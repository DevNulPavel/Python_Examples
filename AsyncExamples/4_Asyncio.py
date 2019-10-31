#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import os
import time

async def printNums():
    num = 1
    while True:
        print(num)
        num += 1
        await asyncio.sleep(0.5)

async def printTime():
    seconds = 0
    while True:
        await asyncio.sleep(1)
        seconds += 1
        if seconds % 3 == 0:
            print("Seconds have passed: {}".format(seconds))

async def mainLoop():
    task1 = asyncio.create_task(printNums())
    task2 = asyncio.create_task(printTime())

    await asyncio.gather(task1, task2)


def timeMain():
    asyncio.run(mainLoop())


####################################################################################

URL = "https://loremflickr.com/320/240"

def writeData(data):
    if os.path.exists("res") == False:
        os.makedirs("res")

    filename = os.path.join("res", "{}.jpeg".format(int(time.time() * 1000)))
    with open(filename, "wb") as f:
        f.write(data)


async def requestFile(session, url):
    async with session.get(url) as result:
        data = await result.read()
        writeData(data)


async def httpMain():
    async with aiohttp.ClientSession() as session:
        tasks = []

        for i in range(5):
            task = asyncio.create_task(requestFile(session, URL))
            tasks.append(task)

        await asyncio.gather(*tasks)


####################################################################################


if __name__ == '__main__':
    asyncio.run(httpMain())