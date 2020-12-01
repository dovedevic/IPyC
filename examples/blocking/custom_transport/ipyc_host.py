import logging
from ipyc import IPyCHost

logging.basicConfig(level=logging.DEBUG)
host = IPyCHost(limit_connections=1)

client = host.wait_for_client()

message = "Hello Client!"
print('Sending to the client:', message)
client.send(message)
response = client.receive()
print("The client sent us a", type(response), ":", response)

client.close()
host.close()
