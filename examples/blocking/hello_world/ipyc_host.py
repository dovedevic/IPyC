import logging
from ipyc import IPyCHost, IPyCSerialization
from custom_object import CustomObject

logging.basicConfig(level=logging.DEBUG)
host = IPyCHost(limit_connections=1)

IPyCSerialization.add_custom_serialization(CustomObject, CustomObject.serialize)
IPyCSerialization.add_custom_deserialization(CustomObject, CustomObject.deserialize)

client = host.wait_for_client()

message = "Please provide a CustomObject!"
print('Sending to the client:', message)
client.send(message)
response = client.receive()
print("The client sent us a", type(response), ":", response)

client.close()
host.close()
