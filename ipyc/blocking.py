import logging

from multiprocessing.connection import Listener, Client

from .links import IPyCLink


class IPyCHost:
    """Represents an abstracted synchronous socket listener that connects with
    and listens to :class:`IPyCClient` clients.
    A number of options can be passed to the :class:`IPyCHost`.
    Parameters
    -----------
    ip_address: Optional[:class:`str`]
        The IP address start listening on. This defaults to ``localhost``.
    port: Optional[:class:`int`]
        The port the listener binds to. This defaults to ``9999``. Check
        your system to make sure this port is not used by another service.
        To use multiple :class:`AsyncIPyCHost` hosts, ensure the ports are
        different between instantiations.
    """
    def __init__(self, ip_address: str='localhost', port:  int=9999):
        self._ip_address = ip_address
        self._port = port
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info(f"Binding to address {ip_address}:{port}")
        self._server = Listener((ip_address, port))
        self._closed = False
        self._connections = set()

    def is_closed(self):
        """:class:`bool`: Indicates if the underlying socket listener is closed or no longer listening."""
        return self._closed

    @property
    def connections(self):
        """:class:`set`: Returns the set of all active :class:`IPyCLink` connections the host is handling."""
        return self._connections

    def close(self):
        """Closes all :class:`IPyCLink` connections and stops the internal listener.
        """
        if self._closed:
            return
        self._closed = True
        for connection in list(self.connections):
            connection.close()
        self._server.close()

    def wait_for_client(self):
        self._logger.info("Starting to wait for a client...")
        if not self.is_closed():
            connection = IPyCLink(self._server.accept(), self)
            self._connections.add(connection)
            return connection


class IPyCMaster(IPyCHost):
    """Pseudo-class for IPyCHost"""
    pass


class IPyCClient:
    """Represents an abstracted synchronous socket client that connects to
    and communicates with :class:`IPyCHost` hosts.
    A number of options can be passed to the :class:`IPyCClient`.
    Parameters
    -----------
    ip_address: Optional[:class:`str`]
        The IP address to connect to. This defaults to ``localhost``.
    port: Optional[:class:`int`]
        The port to target at the host IP address. This defaults to ``9999``.
    """
    def __init__(self, ip_address: str='localhost', port:  int=9999):
        self._ip_address = ip_address
        self._port = port
        self._logger = logging.getLogger(self.__class__.__name__)
        self._link = None
        self._closed = False

    def close(self):
        """Closes the :class:`IPyCLink` connection and stops the client connection."""
        if self._closed:
            return
        self._closed = True
        if self._link:
            self._link.close()
        self._link = None

    def connect(self):
        """A shorthand coroutine for :meth:`asyncio.open_connection`. Any
        arguments supplied are passed to :ref:`asyncio.open_connection()`
        See the asyncio documentation for these arguments and their use.

        Returns
        -------
        :class:`IPyCLink`
            The connection that has been established with a :class:`IPyCHost`.
        """
        self._logger.info("Starting to connect to the host...")
        connection = Client((self._ip_address, self._port))
        self._link = IPyCLink(connection, self)
        return self._link

    @property
    def connections(self):
        """:class:`set`: Returns the set of all active :class:`IPyCLink` connections the client is handling.
        The number of connections is always either one or none.
        """
        return {self._link} if self._link else None


class IPyCSlave(IPyCClient):
    """Pseudo-class for IPyCClient"""
    pass
