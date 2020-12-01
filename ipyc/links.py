import logging

from multiprocessing.connection import Connection

from .headers import CommunicationHeader
from . import serialization


class IPyCLink:
    def __init__(self, connection: Connection):
        self.__connection = connection
        self.__active = True
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__logger.debug(f"[IPyCLink] Established link")

    def close(self):
        self.__logger.debug(f"[IPyCLink] Closing link")
        self.__connection.close()
        self.__active = False

    def send(self, serializable_object):
        if not self.__active:
            return

        if type(serializable_object).__name__ not in serialization.IPYC_CUSTOM_SERIALIZATIONS:
            serialized_string = str(serializable_object)
        else:
            serialized_string = serialization.IPYC_CUSTOM_SERIALIZATIONS[type(serializable_object).__name__](serializable_object)

        if len(type(serializable_object).__name__) > 512:
            raise AssertionError(f"The class name '{type(serializable_object)}' is greater than 512 characters.")

        header = CommunicationHeader(type(serializable_object).__name__, len(serialized_string))
        self.__logger.debug(f"[IPyCLink] Sending communication header for {header.class_size} bytes of '{header.class_name}'")
        self.__connection.send(header.construct().encode())
        self.__logger.debug(f"[IPyCLink] Sending {header.class_size} bytes of '{header.class_name}' data")
        self.__connection.send(serialized_string.encode())

    def receive(self, wait_for_valid=True):
        if not self.__active:
            return None

        def get_header():
            self.__logger.debug(f"[IPyCLink] Waiting for communication header")
            try:
                _ = self.__connection.recv_bytes(1024)
            except Exception as exp:
                # If an exception occurs because we closed the link, silently ignore
                if self.__active:
                    raise exp
                else:
                    _ = ""
            __ = CommunicationHeader.extract(_[4:-3].decode())
            self.__logger.debug(f"[IPyCLink] Communication header was invalid") if __ else None
            return __

        header = get_header()
        while wait_for_valid and not header and self.__active:
            header = get_header()
        if not header or not self.__active:
            return None
        self.__logger.debug(f"[IPyCLink] Waiting for data")
        try:
            data = self.__connection.recv_bytes(header.class_size + 8)
        except Exception as ex:
            # If an exception occurs because we closed the link, silently ignore
            if self.__active:
                raise ex
            else:
                return None
        self.__logger.debug(f"[IPyCLink] Got {header.class_size} bytes of '{header.class_name}'")
        if header.class_name not in serialization.IPYC_CUSTOM_DESERIALIZATIONS:
            return eval(header.class_name)(data[4:-3].decode())
        else:
            return serialization.IPYC_CUSTOM_DESERIALIZATIONS[header.class_name](data[4:-3].decode())
