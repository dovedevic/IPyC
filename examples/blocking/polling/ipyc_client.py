import logging

from ipyc import IPyCClient

# logging.basicConfig(level=logging.DEBUG)

print(f'Connecting to the keep alive server...', end=' ')
client = IPyCClient()
link = client.connect()
print(f'connected! Type [RETURN] to exit.')
while link.is_active():
    message = input("SEND < ")
    if message == '':
        client.close()
        continue
    link.send(message)
    echo = link.receive()
    if echo:
        print(f"RESP > {echo}")
