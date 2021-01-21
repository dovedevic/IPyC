import asyncio
import logging
import sys

from multiprocessing.connection import Connection

from .packets import CommunicationPacket
from . import serialization


class IPyCLink:
    def __init__(self, connection: Connection):
        self.__connection = connection
        self.__active = True
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__logger.debug(f"Established link")

    def close(self):
        self.__logger.debug(f"Closing link")
        self.__connection.close()
        self.__active = False

    def send(self, serializable_object):
        if not self.__active:
            return

        if type(serializable_object).__name__ not in serialization.IPYC_CUSTOM_SERIALIZATIONS:
            serialized_string = str(serializable_object)
        else:
            serialized_string = serialization.IPYC_CUSTOM_SERIALIZATIONS[type(serializable_object).__name__](serializable_object)

        packet = CommunicationPacket(type(serializable_object).__name__, serialized_string)
        self.__logger.debug(f"Sending communication packet for {len(packet.object_serialization)} bytes of '{packet.class_name}'")
        self.__connection.send(header.construct().encode())
        self.__logger.debug(f"Sending {header.class_size} bytes of '{header.class_name}' data")
        self.__connection.send(serialized_string.encode())

    def receive(self, wait_for_valid=True):
        if not self.__active:
            return None

        def get_header():
            self.__logger.debug(f"Waiting for communication header")
            try:
                _ = self.__connection.recv_bytes(1024)
            except Exception as exp:
                # If an exception occurs because we closed the link, silently ignore
                if self.__active:
                    raise exp
                else:
                    _ = ""
            __ = CommunicationHeader.extract(_[4:-3].decode())
            self.__logger.debug(f"Communication header was invalid") if __ else None
            return __

        header = get_header()
        while wait_for_valid and not header and self.__active:
            header = get_header()
        if not header or not self.__active:
            return None
        self.__logger.debug(f"Waiting for data")
        try:
            data = self.__connection.recv_bytes(header.class_size + 8)
        except Exception as ex:
            # If an exception occurs because we closed the link, silently ignore
            if self.__active:
                raise ex
            else:
                return None
        self.__logger.debug(f"Got {header.class_size} bytes of '{header.class_name}'")
        if header.class_name not in serialization.IPYC_CUSTOM_DESERIALIZATIONS:
            return eval(header.class_name)(data[4:-3].decode())
        else:
            return serialization.IPYC_CUSTOM_DESERIALIZATIONS[header.class_name](data[4:-3].decode())


class AsyncIPyCLink:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client):
        self._reader = reader
        self._writer = writer
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f"Established link")
        self._active = True
        self._client = client

    async def close(self):
        self._logger.debug(f"Beginning to close link")
        self._reader = None
        if self._writer.can_write_eof():
            self._writer.write_eof()
            try:
                await self._writer.drain()
            except ConnectionAbortedError:
                pass
        self._writer.close()
        if sys.version_info >= (3, 7):
            await self._writer.wait_closed()
        self._writer = None
        self._active = False
        self._client.connections.remove(self)
        self._logger.debug(f"Closed link")

    def is_active(self):
        # Quickly check if the state of the reader changed from the remote
        if not self._reader or self._reader.at_eof() or not self._writer:
            self._active = False
        return self._active

    async def send(self, serializable_object, drain_immediately=True, encoding='utf-8'):
        if not self.is_active():
            self._logger.debug(f"Attempted to send data when the writer or link is closed! Ignoring.")
            return

        if type(serializable_object).__name__ not in serialization.IPYC_CUSTOM_SERIALIZATIONS:
            self._logger.debug(f"Serializing {type(serializable_object).__name__} as a default python type")
            serialized_string = str(serializable_object)
        else:
            self._logger.debug(f"Serializing {type(serializable_object).__name__} using a custom defined serialization")
            serialized_string = serialization.IPYC_CUSTOM_SERIALIZATIONS[type(serializable_object).__name__](serializable_object)

        packet = CommunicationPacket(type(serializable_object).__name__, serialized_string)
        self._logger.debug(f"Sending {len(packet.object_serialization)} bytes of '{packet.class_name}'")
        self._writer.write(packet.construct(encoding=encoding))
        if drain_immediately:
            self._logger.debug(f"Draining the writer")
            await self._writer.drain()

    async def receive(self, encoding='utf-8', return_on_error=False) -> object:
        if not self.is_active():
            self._logger.debug(f"Attempted to read data when the writer or link is closed! Returning nothing.")
            return None

        self._logger.debug(f"Waiting for communication from the other side")
        try:
            data = await self._reader.readline()
        except ConnectionAbortedError:
            self._logger.debug(f"The downstream connection was aborted")
            await self.close()
            return None
        packet = CommunicationPacket.extract(data, encoding=encoding)
        while not packet and not return_on_error:
            self._logger.debug(f"Packet received was not a valid communication packet... waiting for another")
            if self._reader.at_eof():
                self._logger.debug(f"The downstream writer closed the connection")
                await self.close()
                return None
            try:
                data = await self._reader.readline()
            except ConnectionAbortedError:
                self._logger.debug(f"The downstream connection was aborted")
                await self.close()
                return None
            packet = CommunicationPacket.extract(data, encoding=encoding)
        if self._reader.at_eof():
            self._logger.debug(f"The downstream writer closed the connection")
            await self.close()
            return None
        if not packet:
            self._logger.debug(f"Packet received was not a valid communication packet, return_on_error was set to true. Returning.")
            return None

        self._logger.debug(f"Received {len(packet.object_serialization)} bytes of '{packet.class_name}'")
        if packet.class_name not in serialization.IPYC_CUSTOM_DESERIALIZATIONS:
            return eval(packet.class_name)(packet.object_serialization)
        else:
            return serialization.IPYC_CUSTOM_DESERIALIZATIONS[packet.class_name](packet.object_serialization)
