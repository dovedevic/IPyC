import logging
from ipyc import IPyCClient

logging.basicConfig(level=logging.DEBUG)
client = IPyCClient()

host = client.connect()

response = host.receive()
print("The host sent us a", type(response), ":", response)
message = "Hello Host!"
print('Sending to the host:', message)
host.send(message)

host.close()
client.close()
