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
    print(f"[{datetime.datetime.now()}] - Connection {connection_idx} was closed!")
