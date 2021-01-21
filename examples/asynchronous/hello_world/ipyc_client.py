import logging
import asyncio

from ipyc import AsyncIPyCClient

# logging.basicConfig(level=logging.DEBUG)

async def hello_world():
    print(f'Connecting to the host...', end=' ')
    client = AsyncIPyCClient()
    link = await client.connect()
    print(f'connected!\nSending "Hello World!"...', end=' ')
    await link.send("Hello World!")
    print(f'sent!\nClosing connection...', end=' ')
    await client.close()
    print(f'closed!')

loop = asyncio.get_event_loop()
loop.run_until_complete(hello_world())
