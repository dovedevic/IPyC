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

            if message == 'SHUTDOWN':
                await connection.send(f"SHUTDOWN STARTED")
                print(f"[{datetime.datetime.now()}] - Received a shutdown command!")
                await host.close()
                continue

            await connection.send(f"echo'd {message}")
            print(f"[{datetime.datetime.now()}] - Connection {connection_idx} echo'd!")

    print(f"[{datetime.datetime.now()}] - Connection {connection_idx} was closed!")


print('Starting to wait for connections!')
host.run()
print('Done.')
