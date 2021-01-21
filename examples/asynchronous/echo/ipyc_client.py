import logging
import asyncio

from ipyc import AsyncIPyCClient

# logging.basicConfig(level=logging.DEBUG)

async def echo_me():
    print(f'Connecting to the echo server...', end=' ')
    client = AsyncIPyCClient()
    link = await client.connect()
    print(f'connected! Type [RETURN] to exit.')
    while link.is_active():
        message = input("SEND < ")
        if message == '':
            await client.close()
            continue
        await link.send(message)
        echo = await link.receive()
        if echo:
            print(f"ECHO > {echo}")

loop = asyncio.get_event_loop()
loop.run_until_complete(echo_me())
