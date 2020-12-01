import logging

from multiprocessing.connection import Listener, Client

from .links import IPyCLink


class IPyCHost:
    def __init__(self, ip_address: str='localhost', port:  int=9999, authentication_password: bytes=None, start_listening=False, limit_connections=None):
        self.__ip_address = ip_address
        self.__port = port
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__continue_listening = True
        self.__limit_connections = limit_connections or -1
        self.__connections = []

        self.__logger.info(f"Binding to address {ip_address}:{port}{' with auth' if authentication_password else ''}")
        self.__listener = Listener((ip_address, port), authkey=bytes(authentication_password) if authentication_password else None)

        if start_listening:
            self.wait_for_client()

    def close(self):
        self.__listener.close()
        for connection in self.__connections:
            connection.close()

    def wait_for_client(self):
        self.__logger.info("[IPyCHost] Starting to wait for a client...")
        if self.__continue_listening and (self.__limit_connections > 0 or self.__limit_connections == -1):
            connection = IPyCLink(self.__listener.accept())
            if self.__limit_connections != -1:
                self.__limit_connections -= 1
            self.__connections.append(connection)
            self.__logger.debug("[IPyCHost] Successfully connected to the client")
            return connection
        elif not self.__continue_listening:
            raise ConnectionRefusedError("Cannot connect to any more clients since the host client was instructed to stop.")
        elif self.__limit_connections == 0 and self.__limit_connections != -1:
            raise ConnectionRefusedError("Cannot connect to any more clients since the number of allowed connections was spent.")


class IPyCMaster(IPyCHost):
    """
    Pseudo-class for IPyCHost
    """
    pass


class IPyCClient:
    def __init__(self, ip_address: str='localhost', port:  int=9999, authentication_password: bytes=None, start_connecting=False):
        self.__ip_address = ip_address
        self.__port = port
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__connection = None
        self.__stored_auth = authentication_password

        if start_connecting:
            self.connect()

    def close(self):
        if self.__connection:
            self.__connection.close()

    def connect(self):
        self.__logger.info("[IPyCClient] Starting to connect to the host...")
        connection = Client((self.__ip_address, self.__port), authkey=bytes(self.__stored_auth) if self.__stored_auth else None)
        self.__connection = IPyCLink(connection)
        del self.__stored_auth
        self.__logger.debug("[IPyCClient] Successfully connected to the host")
        return self.__connection

    @property
    def connection(self):
        return self.__connection


class IPyCSlave(IPyCClient):
    """
    Pseudo-class for IPyCClient
    """
    pass
