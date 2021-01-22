import logging
import datetime

from ipyc import IPyCHost, IPyCLink

host = IPyCHost()
# logging.basicConfig(level=logging.DEBUG)

print('Starting to wait for connections!')
while not host.is_closed():
    connection = host.wait_for_client()
    connection_idx = len(host.connections)

    print(f'We got a new connection! ({connection_idx})')
    while connection.is_active():
        message = connection.receive()
        if message:
            print(f"[{datetime.datetime.now()}] - Connection {connection_idx} says: {message}")

            if message == 'SHUTDOWN':
                connection.send(f"SHUTDOWN STARTED")
                print(f"[{datetime.datetime.now()}] - Received a shutdown command!")
                host.close()
                continue

            connection.send(f"echo'd {message}")
            print(f"[{datetime.datetime.now()}] - Connection {connection_idx} echo'd!")

    print(f"[{datetime.datetime.now()}] - Connection {connection_idx} was closed!")

print('Done.')
