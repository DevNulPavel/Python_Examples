#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import os
import time
import concurrent.futures

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

async def cancelableFunc(delay):
    #print("Before sleep")
    try:
        await asyncio.sleep(delay)
        return delay
    except asyncio.CancelledError:
        #print("Sleep canceled")
        raise
    finally:
        #print("After sleep")
        pass


async def someExamplesMain():
    # Создаем задачу
    delayedTask = asyncio.create_task(cancelableFunc(30))

    # Засыпаем
    await asyncio.sleep(1)

    # Отменяем задачу, внутри выбрасывается исключение на очередной await команде
    delayedTask.cancel()

    # Можно проверить - была ли уже завершена задача или нет?
    isCanceled = delayedTask.cancelled()
    print("Is canceled: {0}".format(isCanceled))

    # Можно проверить - готова ли задача или нет
    isDone = delayedTask.done()
    print("Is done: {0}".format(isDone))
    if isDone:
        # Можно получить результат работы
        result = delayedTask.result()
        print("Task result: {0}".format(result))

    try:
        #TODO: ???
        # Защита задачи от отмены???
        res = await asyncio.shield(delayedTask)
        print("Delayed {0} seconds".format(res))
    except asyncio.CancelledError:
        print("Canceled")

    # Можно ждать завершения корутины какое-то определенное время
    delayedTask = asyncio.create_task(cancelableFunc(40))
    try:
        # При таймауте вызывается cancel у задачи
        res = await asyncio.wait_for(delayedTask, timeout=1.0)
        print("Delayed {0} seconds".format(res))
    except asyncio.TimeoutError:
        print("Wait timeout")

    # Можно дождаться завершения работы какой-то корутины из списка
    # В отличие от wait_for(), wait() не отменяет задачу при таймауте
    waitTask1 = asyncio.create_task(cancelableFunc(3))
    waitTask2 = asyncio.create_task(cancelableFunc(5))
    completed, pending = await asyncio.wait([waitTask1, waitTask2], timeout=None, return_when=asyncio.FIRST_COMPLETED)
    if waitTask1 in completed:
        res = await waitTask1
        print("First completed: {0}".format(res))
    if waitTask2 in pending:
        print("Second is pending")

    # Можно итерироваться по фьючам, чтобы постепенно получать результаты работы из каждой из них
    waitTask3 = asyncio.create_task(cancelableFunc(3))
    waitTask4 = asyncio.create_task(cancelableFunc(5))
    for future in asyncio.as_completed([waitTask3, waitTask4]):
        res = await future
        print("Iterate result: {0}".format(res))


####################################################################################


def blockingIO():
    # File operations (such as logging) can block the
    # event loop: run them in a thread pool.
    with open('/dev/urandom', 'rb') as f:
        return f.read(100)

def cpuBound():
    # CPU-bound operations will block the event loop:
    # in general it is preferable to run them in a
    # process pool.
    return sum(i * i for i in range(10 ** 7))

async def cpuCodeMain():
    loop = asyncio.get_running_loop()

    # Запуск в стандарном исполнителе
    result = await loop.run_in_executor(None, blockingIO)
    print("Default thread pool", result)

    # Запуск в кастомном пуле потоков
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blockingIO)
        print("Custom thread pool", result)

    # Запуск в кастомном пуле процессов
    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpuBound)
        print("Custom process pool", result)


####################################################################################


if __name__ == '__main__':
    asyncio.run(cpuCodeMain())