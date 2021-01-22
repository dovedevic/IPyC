import logging
import datetime

from ipyc import IPyCHost, IPyCLink, IPyCSerialization


class CustomObject:
    def __init__(self, arg1: int, arg2: float, arg3: str, arg4: set):
        self.a1 = arg1
        self.a2 = arg2
        self.a3 = arg3
        self.a4 = arg4

    def __str__(self):
        return f"<CustomObject:a1={self.a1},a2={self.a2},a3={self.a3},a4={self.a4}>"

    # Define a serializer that returns a string/str representation of the object
    def serialize(self):
        return f"{self.a1}|{self.a2}|{self.a3}|{self.a4}"

    # Define a deserializer that undoes what the serializer did and returns the object
    @staticmethod
    def deserialize(serialization):
        a1, a2, a3, a4 = serialization.split('|')
        return CustomObject(int(a1), float(a2), str(a3), eval(a4))


# logging.basicConfig(level=logging.DEBUG)
host = IPyCHost()
IPyCSerialization.add_custom_deserialization(CustomObject, CustomObject.deserialize)

print('Starting to wait for connections!')
while not host.is_closed():
    connection = host.wait_for_client()
    connection_idx = len(host.connections)

    print(f'We got a new connection! ({connection_idx})')
    while connection.is_active():
        message = connection.receive()
        if message:
            print(f"[{datetime.datetime.now()}] - Connection {connection_idx} sent us a {type(message)} and it was {message}")
            print(message.a1, message.a2, message.a3, message.a4)
    print(f"[{datetime.datetime.now()}] - Connection {connection_idx} was closed!")
