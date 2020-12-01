import logging
from ipyc import IPyCClient, IPyCSerialization
from custom_object import CustomObject

logging.basicConfig(level=logging.DEBUG)
client = IPyCClient()

IPyCSerialization.add_custom_serialization(CustomObject, CustomObject.serialize)
IPyCSerialization.add_custom_deserialization(CustomObject, CustomObject.deserialize)

host = client.connect()

response = host.receive()
print("The host sent us a", type(response), ":", response)
obj = CustomObject(42, 3.14159, "Here you go!", {1, 2, 5, 8})
print('Sending to the host:', obj)
host.send(obj)

host.close()
client.close()
