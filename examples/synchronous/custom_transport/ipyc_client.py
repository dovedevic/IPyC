import logging

from ipyc import IPyCClient, IPyCSerialization


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
custom_object = CustomObject(42, 3.1415926535897932, "Lorem ipsum dolor sit amet", {'s', 'e', 't'})
IPyCSerialization.add_custom_serialization(CustomObject, CustomObject.serialize)


print(f'Connecting to the host...', end=' ')
client = IPyCClient()
link = client.connect()
print(f'connected!\nSending {custom_object}...', end=' ')
link.send(custom_object)
print(f'sent!\nClosing connection...', end=' ')
client.close()
print(f'closed!')
