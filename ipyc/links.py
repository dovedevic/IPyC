import asyncio
import logging
import sys

from multiprocessing.connection import Connection

from .packets import CommunicationPacket
from . import serialization


class IPyCLink:
    """Represents an abstracted synchronous socket connection that handles
    communication between a :class:`IPyCHost` and a :class:`IPyCClient`
    This class is internally managed and typically should not be instantiated on
    its own.

    Parameters
    -----------
    connection: :class:`multiprocessing.connection.Connection`
        The managed socket connection.
    client: Union[:class:`IPyCHost`, :class:`IPyCClient`]
        The communication object that is responsible for managing this connection.
    """
    def __init__(self, connection: Connection, client):
        self._connection = connection
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f"Established link")
        self._active = True
        self._client = client

    def close(self):
        """Closes the socket channel with a peer and attempts to send them EOF.
        Informs the parent :class:`IPyCHost` or :class:`IPyCClient` of the
        closed connection.
        """
        self._logger.debug(f"Beginning to close link")
        self._connection.close()
        self._active = False
        self._client.connections.remove(self)
        self._logger.debug(f"Closed link")

    def is_active(self):
        """:class:`bool`: Indicates if the socket connection is closed, at EOF, or no longer viable."""
        # Quickly check if the state of the reader changed from the remote
        if not self._connection or self._connection.closed:
            self._active = False
        return self._active

    def send(self, serializable_object: object, encoding='utf-8'):
        """Send a serializable object to the receiving end. If the object is not a custom
        serializable object, python's builtins will be used. If the object is a custom
        serializable, the receiving end must also have this object in their list of custom
        deserializers.

        .. warning::
            After the result of serialization, either via custom or builtin, the bytes ``0x01`` and ``0x02``
            must not appear anywhere. If your payload does contain these bytes or chars, you must
            substitute them prior to this function call.

        Parameters
        ------------
        serializable_object: :class:`object`
            The object to be sent to the receiving end.
        encoding: Optional[:class:`str`]
            The encoding schema of the serialization. If your object serialization results
            in non UTF-8 encoding characters, a different encoding scheme must be used. The
            receiving end must also use this same encoding to decode properly.
            Defaults to ``utf-8``.

        """
        if not self.is_active():
            self._logger.debug(f"Attempted to send data when the link is closed! Ignoring.")
            return

        if type(serializable_object).__name__ not in serialization.IPYC_CUSTOM_SERIALIZATIONS:
            self._logger.debug(f"Serializing {type(serializable_object).__name__} as a default python type")
            serialized_string = str(serializable_object)
        else:
            self._logger.debug(f"Serializing {type(serializable_object).__name__} using a custom defined serialization")
            serialized_string = serialization.IPYC_CUSTOM_SERIALIZATIONS[type(serializable_object).__name__](serializable_object)

        packet = CommunicationPacket(type(serializable_object).__name__, serialized_string)
        self._logger.debug(f"Sending {len(packet.object_serialization)} bytes of '{packet.class_name}'")
        self._connection.send(packet.construct(encoding=encoding))

    def receive(self, encoding='utf-8', return_on_error=False):
        """Receive a serializable object from the other end. If the object is not a custom
        serializable object, python's builtins will be used, otherwise the custom defined
        deserializer will be used.

        Parameters
        ------------
        encoding: Optional[:class:`str`]
            The encoding schema of the serialization. If your object serialization results
            in non UTF-8 encoding characters, a different encoding scheme must be used. The
            receiving end must also use this same encoding to decode properly.
            Defaults to ``utf-8``.
        return_on_error: Optional[:class:`bool`]
            Whether to continue to listen or return if a deserialization error occurred. Otherwise,
            wait until the next valid deserialization occurs.
            Defaults to ``False``.

        Returns
        --------
        Optional[:class:`object`]
            The object that was sent from the sending end. If the deserialization was not successful
            and ``return_on_error`` was set to ``True``, or EOF was encountered resulting in a closed
            connection, ``None`` is returned.
        """
        if not self.is_active():
            self._logger.debug(f"Attempted to read data when link is closed! Returning nothing.")
            return None

        self._logger.debug(f"Waiting for communication from the other side")
        try:
            data = self._connection.recv()
        except (EOFError, ConnectionAbortedError):
            self._logger.debug(f"The downstream connection was aborted")
            self.close()
            return None
        packet = CommunicationPacket.extract(data, encoding=encoding)
        while not packet and not return_on_error:
            self._logger.debug(f"Packet received was not a valid communication packet... waiting for another")
            if self._connection.closed:
                self._logger.debug(f"The downstream connection was closed")
                self.close()
                return None
            try:
                data = self._connection.recv()
            except (EOFError, ConnectionAbortedError):
                self._logger.debug(f"The downstream connection was aborted")
                self.close()
                return None
            packet = CommunicationPacket.extract(data, encoding=encoding)
        if self._connection.closed:
            self._logger.debug(f"The downstream connection as closed")
            self.close()
            return None
        if not packet:
            self._logger.debug(f"Packet received was not a valid communication packet, return_on_error was set to true. Returning.")
            return None

        self._logger.debug(f"Received {len(packet.object_serialization)} bytes of '{packet.class_name}'")
        if packet.class_name not in serialization.IPYC_CUSTOM_DESERIALIZATIONS:
            return eval(packet.class_name)(packet.object_serialization)
        else:
            return serialization.IPYC_CUSTOM_DESERIALIZATIONS[packet.class_name](packet.object_serialization)

    def poll(self, timeout=0.0):
        """Return whether there is any data available to be read from the downstream connection.

        Parameters
        ------------
        timeout: Optional[:class:`float`]
            The number of seconds to wait to see if data is available. If set to ``None``, poll will block
            forever until data is ready to be read. If set to ``0``, return a result immediately.
            Defaults to ``0.0``.

        Returns
        --------
        :class:`bool`
            ``True`` if data is ready to be received, ``False`` otherwise.
        """
        return self._connection.poll(timeout=timeout)


class AsyncIPyCLink:
    """Represents an abstracted async socket connection that handles
    communication between a :class:`AsyncIPyCHost` and a :class:`AsyncIPyCClient`
    This class is internally managed and typically should not be instantiated on
    its own.

    Parameters
    -----------
    reader: :class:`asyncio.StreamReader`
        The managed inbound data reader.
    writer: :class:`asyncio.StreamWriter`
        The managed outbound data writer
    client: Union[:class:`AsyncIPyCHost`, :class:`AsyncIPyCClient`]
        The communication object that is responsible for managing this connection.
    """
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, client):
        self._reader = reader
        self._writer = writer
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f"Established link")
        self._active = True
        self._client = client

    async def close(self):
        """|coro|

        Closes all communication channels with a peer and attempts to send them EOF.
        Informs the parent :class:`AsyncIPyCHost` or :class:`AsyncIPyCClient` of the
        closed connection.
        """
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
        """:class:`bool`: Indicates if the communication channels are closed, at EOF, or no longer viable."""
        # Quickly check if the state of the reader changed from the remote
        if not self._reader or self._reader.at_eof() or not self._writer:
            self._active = False
        return self._active

    async def send(self, serializable_object: object, drain_immediately=True, encoding='utf-8'):
        """|coro|

        Send a serializable object to the receiving end. If the object is not a custom
        serializable object, python's builtins will be used. If the object is a custom
        serializable, the receiving end must also have this object in their list of custom
        deserializers.

        .. warning::
            After the result of serialization, either via custom or builtin, the bytes ``0x01`` and ``0x02``
            must not appear anywhere. If your payload does contain these bytes or chars, you must
            substitute them prior to this function call.

        Parameters
        ------------
        serializable_object: :class:`object`
            The object to be sent to the receiving end.
        drain_immediately: Optional[:class:`bool`]
            Whether to flush the output buffer right now or not.
            Defaults to ``True``.
        encoding: Optional[:class:`str`]
            The encoding schema of the serialization. If your object serialization results
            in non UTF-8 encoding characters, a different encoding scheme must be used. The
            receiving end must also use this same encoding to decode properly.
            Defaults to ``utf-8``.

        """
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

    async def receive(self, encoding='utf-8', return_on_error=False):
        """|coro|

        Receive a serializable object from the other end. If the object is not a custom
        serializable object, python's builtins will be used, otherwise the custom defined
        deserializer will be used.

        Parameters
        ------------
        encoding: Optional[:class:`str`]
            The encoding schema of the serialization. If your object serialization results
            in non UTF-8 encoding characters, a different encoding scheme must be used. The
            receiving end must also use this same encoding to decode properly.
            Defaults to ``utf-8``.
        return_on_error: Optional[:class:`bool`]
            Whether to continue to listen or return if a deserialization error occurred. Otherwise,
            wait until the next valid deserialization occurs.
            Defaults to ``False``.

        Returns
        --------
        Optional[:class:`object`]
            The object that was sent from the sending end. If the deserialization was not successful
            and ``return_on_error`` was set to ``True``, or EOF was encountered resulting in a closed
            connection, ``None`` is returned.
        """
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
