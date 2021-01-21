class CommunicationPacket:
    def __init__(self, class_name: str, object_serialization: str):
        self.__name = class_name
        self.__object_serialization = object_serialization

    @property
    def class_name(self):
        return self.__name

    @property
    def object_serialization(self):
        return self.__object_serialization

    def construct(self, encoding: str) -> bytes:
        return "\x01{}\x02{}\n".format(self.__name, self.__object_serialization.replace('\n', '\x1a')).encode(encoding)

    @staticmethod
    def extract(packet: bytes, encoding: str):
        try:
            packet = packet.decode(encoding)
            if not packet.startswith('\x01') or not packet.endswith('\n'):
                raise ValueError
            serialization_string = packet[1:-1]
            name, serialization = serialization_string.split('\x02')
            return CommunicationPacket(name, serialization.replace('\x1a', '\n'))
        except (MemoryError, RuntimeError, ValueError, UnicodeError, UnicodeDecodeError):
            return None
