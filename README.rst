IPyC - Python InterProcess Communication
========================================

.. image:: https://img.shields.io/pypi/v/IPyC.svg
   :target: https://pypi.python.org/pypi/IPyC
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/IPyC.svg
   :target: https://pypi.python.org/pypi/IPyC
   :alt: PyPI supported Python versions

An elegant and modern Python IPC implementation using multiprocessing and asyncio. IPyC comes in two flavors, synchronous and asynchronous, both using the same backend allowing you to pick and chose to your needs.

Send builtins, custom objects, and more!

Key Features
------------

- Uses the modern ``async`` and ``await`` AsyncIO Python API.
- Includes a synchronous version for backward compatibility.
- Flexible, easy to install, setup, and use.
- Can transfer custom objects and classes at runtime!

Installing
----------

**Python 3.5.3 or higher is required if you use the asynchronous version**

To install the library you can just run the following command:

.. code:: sh

    # In general
    pip3 install IPyC

    # Linux/macOS
    python3 -m pip install -U IPyC

    # Windows
    py -3 -m pip install -U IPyC


Hello World Example (using the asynchronous version)
----------------------------------------------------
Client
~~~~~~

.. code:: py

    import asyncio
    from ipyc import AsyncIPyCClient

    async def hello_world():
        client = AsyncIPyCClient()  # Create a client
        link = await client.connect()  # Connect to the host
        await link.send("Hello World!")  # Send a string
        await client.close()  # Close the connection

    loop = asyncio.get_event_loop()
    loop.run_until_complete(hello_world())

Host
~~~~

.. code:: py

    import datetime
    from ipyc import AsyncIPyCHost, AsyncIPyCLink

    host = AsyncIPyCHost()

    @host.on_connect
    async def on_client_connect(connection: AsyncIPyCLink):
        while connection.is_active():
            message = await connection.receive()
            if message:
                print(f"[{datetime.datetime.now()}] - Client says: {message}")
        print(f"[{datetime.datetime.now()}] - Connection was closed!")

    host.run()

Custom Objects Example (using the synchronous version)
------------------------------------------------------
Custom Object
~~~~~~~~~~~~~

.. code:: py

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

Client
~~~~~~

.. code:: py

    from ipyc import IPyCClient, IPyCSerialization

    custom_object = CustomObject(42, 3.1415926535897932, "Lorem ipsum dolor sit amet", {'s', 'e', 't'})
    IPyCSerialization.add_custom_serialization(CustomObject, CustomObject.serialize)

    client = IPyCClient()
    link = client.connect()
    link.send(custom_object)
    client.close()

Host
~~~~

.. code:: py

    import datetime
    from ipyc import IPyCHost, IPyCLink, IPyCSerialization

    host = IPyCHost()
    IPyCSerialization.add_custom_deserialization(CustomObject, CustomObject.deserialize)

    while not host.is_closed():
        connection = host.wait_for_client()

        while connection.is_active():
            message = connection.receive()
            if message:
                print(f"[{datetime.datetime.now()}] - Client sent us a {type(message)} and it was {message}")
                print(message.a1, message.a2, message.a3, message.a4)
        print(f"[{datetime.datetime.now()}] - Connection was closed!")

You can find more examples in the `examples <https://github.com/dovedevic/IPyC/tree/main/examples>`_ directory.

Useful Links
------------

- `Documentation <https://ipyc.readthedocs.io/en/latest/index.html>`_
- `AsyncIO Documentation <https://docs.python.org/3/library/asyncio.html>`_
- `Multiprocessing Communication Documentation <https://docs.python.org/3/library/multiprocessing.html>`_
