import logging

from ipyc import IPyCClient

# logging.basicConfig(level=logging.DEBUG)

print(f'Connecting to the host...', end=' ')
client = IPyCClient()
link = client.connect()
print(f'connected!\nSending "Hello World!"...', end=' ')
link.send("Hello World!")
print(f'sent!\nClosing connection...', end=' ')
client.close()
print(f'closed!')
