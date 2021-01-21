import logging
import datetime

from ipyc import AsyncIPyCHost, AsyncIPyCLink

host = AsyncIPyCHost()
# logging.basicConfig(level=logging.DEBUG)


@host.on_connect
async def on_connection(connection: AsyncIPyCLink):
    connection_idx = len(host.connections)

    print(f'We got a new connection! ({connection_idx})')
    while connection.is_active():
        message = await connection.receive()
        if message:
            print(f"[{datetime.datetime.now()}] - Connection {connection_idx} says: {message}")
    print(f"[{datetime.datetime.now()}] - Connection {connection_idx} was closed!")


print('Starting to wait for connections!')
host.run()
