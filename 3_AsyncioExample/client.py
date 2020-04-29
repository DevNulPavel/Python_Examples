#! /usr/bin/env python3

import asyncio


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    while True:
        print(f"Send: {message!r}")
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')


    print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def main():
    await tcp_echo_client("Test")


if __name__ == "__main__":
    asyncio.run(main())