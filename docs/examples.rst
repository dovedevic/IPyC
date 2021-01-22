.. _examples:

IPyC Examples and Uses
=======================

When attempting to communicate between any host and client, ensure the host runs first. That is, the host must be
*listening* prior to any client connection.

All examples listed here are also in the examples directory with the installed module. You can view them on the GitHub
or browse to them using your file explorer to view and interact with.

Hello World
--------------------

Host
~~~~~~~

.. code-block:: python3

    from ipyc import AsyncIPyCHost, AsyncIPyCLink

    host = AsyncIPyCHost()

    @host.on_connect
    async def on_connection(connection: AsyncIPyCLink):
        print('We got a new connection!')
        while connection.is_active():
            message = await connection.receive()
            if message:
                print(f"The other side says: {message}")
        print("The connection was closed!")

    print('Starting to wait for connections!')
    host.run()

Client
~~~~~~~

.. code-block:: python3

    import asyncio
    from ipyc import AsyncIPyCClient

    async def hello_world():
        print('Connecting to the host...', end=' ')
        client = AsyncIPyCClient()
        link = await client.connect()
        print('connected!\nSending "Hello World!"...', end=' ')
        await link.send("Hello World!")
        print('sent!\nClosing connection...', end=' ')
        await client.close()
        print('closed!')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(hello_world())

Explanation
~~~~~~~~~~~~~~~~~~~~~~~

This simple set of scripts allows the client to send the host a string that says "Hello World". Since a string is
a pyhton builtin, no custom serializer is needed, and can be send natively. Additionally, it is assumed that these
two applications are run on the same machine, since no IP address was supplied to the host and client classes. If
however these are on two different systems, an IP address must be supplied for the host and client.


Custom Transport
--------------------

Sometimes sending builtins is not enough. Typically classes are built from builtins, but are not natively able to be
"stringified". Because of this, IPyC allows for you to define a custom serializer and deserializer for your custom
classes. These methods can be built into the classes themselves or expressed outside class scope.

The following example will show how you can use IPyC to transport the following class:

.. code-block:: python3

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

Host
~~~~~~~

.. code-block:: python3

    from ipyc import IPyCHost, IPyCLink, IPyCSerialization
    from custom_object import CustomObject

    host = IPyCHost()
    IPyCSerialization.add_custom_deserialization(CustomObject, CustomObject.deserialize)

    print('Starting to wait for connections!')
    while not host.is_closed():
        connection = host.wait_for_client()
        print('We got a new connection!')
        while connection.is_active():
            message = connection.receive()
            if message:
                print(f"The connection sent us a {type(message)} and it was {message}")
                print(message.a1, message.a2, message.a3, message.a4)
        print("The connection was closed!")

Client
~~~~~~~

.. code-block:: python3

    from ipyc import IPyCClient, IPyCSerialization
    from custom_object import CustomObject

    custom_object = CustomObject(42, 3.1415926535897932, "Lorem ipsum dolor sit amet", {'s', 'e', 't'})
    IPyCSerialization.add_custom_serialization(CustomObject, CustomObject.serialize)

    print('Connecting to the host...', end=' ')
    client = IPyCClient()
    link = client.connect()
    print(f'connected!\nSending {custom_object}...', end=' ')
    link.send(custom_object)
    print('sent!\nClosing connection...', end=' ')
    client.close()
    print('closed!')

Explanation
~~~~~~~~~~~~~~~~~~~~~~~

This set of scripts allows the client to send the host a class object. Note however not all objects are able to be
serialized or deserialized; examples of such are stateful connection objects, memory bound objects, and system
specific structures.
