import logging
import time
import datetime

from ipyc import IPyCHost, IPyCLink

host = IPyCHost()
countdown = 30
# logging.basicConfig(level=logging.DEBUG)

print('Starting to wait for connections!')
while not host.is_closed():
    connection = host.wait_for_client()
    connection_idx = len(host.connections)

    print(f'We got a new connection! ({connection_idx})')
    while connection.is_active():
        if not connection.poll():
            countdown -= 1
            if countdown <= 0:
                connection.close()
                continue
            else:
                print(f'No message was received... shutting down in {countdown} seconds')
            time.sleep(1)
        else:
            message = connection.receive()
            if message:
                print(f"[{datetime.datetime.now()}] - Connection {connection_idx} says: {message}")
                countdown = 30
                connection.send(f"Countdown reset to 30s")
                print(f"[{datetime.datetime.now()}] - Connection {connection_idx} keep alive now 30s")

    print(f"[{datetime.datetime.now()}] - Connection {connection_idx} was closed!")
    countdown = 30

print('Done.')
