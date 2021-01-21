import asyncio
import logging
import signal
import sys

from .links import AsyncIPyCLink


class AsyncIPyCHost:
    """Represents an abstracted async socket listener that connects with
    and listens to :class:`AsyncIPyCClient` clients.
    A number of options can be passed to the :class:`AsyncIPyCHost`.
    Parameters
    -----------
    ip_address: Optional[:class:`str`]
        The IP address start listening on. This defaults to ``localhost``.
    port: Optional[:class:`int`]
        The port the listener binds to. This defaults to ``9999``. Check
        your system to make sure this port is not used by another service.
        To use multiple :class:`AsyncIPyCHost` hosts, ensure the ports are
        different between instantiations.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used via
        :func:`asyncio.get_event_loop()`.
    Attributes
    -----------
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop that the client uses for HTTP requests and websocket operations.
    """
    def __init__(self, ip_address: str='localhost', port:  int=9999, loop=None):
        self._ip_address = ip_address
        self._port = port
        self._logger = logging.getLogger(self.__class__.__name__)
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self._server = None
        self._closed = False
        self._connections = set()
        self._handlers = {
            'connect': set()
        }
        self._on_close = asyncio.Event()

    async def __handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        new_connection = AsyncIPyCLink(reader, writer, self)
        self.connections.add(new_connection)
        for handle in self._handlers['connect']:
            await handle(new_connection)

    def _cleanup_loop(self, loop):
        try:
            self._cancel_tasks(loop)
            if sys.version_info >= (3, 6):
                loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            self._logger.debug('Closing the event loop.')
            loop.close()

    def _cancel_tasks(self, loop):
        try:
            task_retriever = asyncio.Task.all_tasks
        except AttributeError:
            # future proofing for 3.9
            task_retriever = asyncio.all_tasks

        tasks = {t for t in task_retriever(loop=loop) if not t.done()}

        if not tasks:
            return

        self._logger.debug('Cleaning up after %d tasks.', len(tasks))
        for task in tasks:
            task.cancel()

        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        self._logger.debug('All tasks finished cancelling.')

        for task in tasks:
            if task.cancelled():
                continue
            if task.exception() is not None:
                loop.call_exception_handler({
                    'message': 'Unhandled exception during AsyncIPyCHost.run shutdown.',
                    'exception': task.exception(),
                    'task': task
                })

    def on_connect(self, coro):
        """A decorator that registers a coroutine to execute when a connection is made to the listener.

        The decorated function must be a :ref:`coroutine <coroutine>` and possess one parameter for the :class:`AsyncIPyCLink` connection link that is supplied on connection; if not, a :exc:`TypeError` is raised.

        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine handler to be called when a new connection is made to the listener
        Example
        ---------
        .. code-block:: python3
            @client.on_connect
            async def connectionMade(link: AsyncIPyCLink):
                print('A connection was made!!')
        Raises
        --------
        TypeError
            The coroutine passed is not actually a coroutine or does not contain enough arguments.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('@on_connect must register a coroutine function')

        if coro.__code__.co_argcount not in [1, 2]:
            raise TypeError('@on_connect coroutines must allow for a Link argument')

        self._handlers['connect'].add(coro)
        self._logger.debug(f'[IPyCHost] {coro.__name__} has successfully been registered as an on_connect event')
        return coro

    def add_connection_handler(self, coro):
        """Wrapped decorator for the :meth:`on_connect` method.

        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine handler to be called when a new connection is made to the listener
        Raises
        --------
        TypeError
            The coroutine passed is not actually a coroutine or does not contain enough arguments.
        """
        self.on_connect(coro)

    def remove_connection_handler(self, coro):
        """Removes a connection handler from the internal listener dispatcher.

        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine handler to be removed.
        """
        if coro in self._handlers['connect']:
            self._handlers['connect'].remove(coro)

    def is_closed(self):
        """:class:`bool`: Indicates if the underlying socket listener is closed or no longer listening."""
        return self._closed

    @property
    def connections(self):
        """:class:`set`: Returns the set of all active :class:`AsyncIPyCLink` connections the host is handling."""
        return self._connections

    async def start(self, *args):
        """|coro|

        A shorthand coroutine for :meth:`asyncio.start_server`. Any
        arguments supplied are passed to :ref:`asyncio.start_server()`
        and afterward to :ref:`loop.create_server()`. See the asyncio
        documentation for these arguments and their use.

        """
        self._server = await asyncio.start_server(self.__handle_connection, host=self._ip_address, port=self._port, loop=self.loop, *args)

    def run(self, *args):
        """A blocking call that begins server listening and abstracts
        away the asyncio event loop initialisation and handling.

        If you want more control over the event loop then this
        function should not be used. Use the :meth:`start`
        coroutine instead.

        Any arguments supplied is directly passed to the
        :meth:`start` coroutine. See it's documentation for use.

        .. warning::

            This function must be the last function to call due to the fact that it
            is blocking. That means that anything being called after this function
            or executed call will not happen until this line closes or terminates.
        """
        try:
            self.loop.add_signal_handler(signal.SIGINT, lambda: self.loop.stop())
            self.loop.add_signal_handler(signal.SIGTERM, lambda: self.loop.stop())
        except NotImplementedError:
            pass

        async def runner():
            try:
                await self.start(*args)
                await self._on_close.wait()
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(_):
            self.loop.stop()

        future = asyncio.ensure_future(runner(), loop=self.loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self._logger.debug('Received signal to terminate bot and event loop.')
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            self._logger.debug('Cleaning up tasks.')
            self._cleanup_loop(self.loop)

        if not future.cancelled():
            try:
                return future.result()
            except KeyboardInterrupt:
                return None

    async def close(self):
        """|coro|

        Closes all :class:`AsyncIPyCLink` connections and stops the internal listener.
        """
        if self._closed:
            return
        self._closed = True
        for connection in list(self.connections):
            await connection.close()
        self._on_close.set()


class AsyncIPyCMaster(AsyncIPyCHost):
    """Pseudo-class for AsyncIPyCHost"""
    pass


class AsyncIPyCClient:
    """Represents an abstracted async socket client that connects to
    and communicates with :class:`AsyncIPyCHost` hosts.
    A number of options can be passed to the :class:`AsyncIPyCClient`.
    Parameters
    -----------
    ip_address: Optional[:class:`str`]
        The IP address to connect to. This defaults to ``localhost``.
    port: Optional[:class:`int`]
        The port to target at the host IP address. This defaults to ``9999``.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used via
        :func:`asyncio.get_event_loop()`.
    Attributes
    -----------
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop that the client uses for HTTP requests and websocket operations.
    """
    def __init__(self, ip_address: str='localhost', port:  int=9999, loop=None):
        self._ip_address = ip_address
        self._port = port
        self._logger = logging.getLogger(self.__class__.__name__)
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self._link = None
        self._closed = False
        self._handlers = {
            'connect': []
        }

    async def connect(self, *args) -> AsyncIPyCLink:
        """|coro|

        A shorthand coroutine for :meth:`asyncio.open_connection`. Any
        arguments supplied are passed to :ref:`asyncio.open_connection()`
        See the asyncio documentation for these arguments and their use.

        Returns
        -------
        :class:`AsyncIPyCLink`
            The connection that has been established with a :class:`AsyncIPyCHost`.
        """
        reader, writer = await asyncio.open_connection(host=self._ip_address, port=self._port, loop=self.loop, *args)
        self._link = AsyncIPyCLink(reader, writer, self)
        return self._link

    async def close(self):
        """|coro|

        Closes the :class:`AsyncIPyCLink` connection and stops the client connection.
        """
        if self._closed:
            return
        self._closed = True
        await self._link.close()
        self._link = None

    @property
    def connections(self):
        """:class:`set`: Returns the set of all active :class:`AsyncIPyCLink` connections the client is handling.
        The number of connections is always either one or none.
        """
        return {self._link} if self._link else None


class AsyncIPyCSlave(AsyncIPyCClient):
    """Pseudo-class for AsyncIPyCClient"""
    pass
