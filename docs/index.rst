.. IPyC documentation master file, created by
   sphinx-quickstart on Fri Jan 22 01:03:30 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IPyC
===========================

An elegant and modern Python IPC implementation using multiprocessing and asyncio.
IPyC comes in two flavors, synchronous and asynchronous, both using the same
backend allowing you to pick and chose to your needs.

**Features:**

- Uses the modern ``async`` and ``await`` AsyncIO Python API.
- Includes a synchronous version for backward compatibility.
- Flexible, easy to install, setup, and use.
- Can transfer custom objects and classes at runtime!


Contents
--------

.. toctree::
   :maxdepth: 2

   ipyc
   asyncipyc
   connection
   serialization
   examples
   logging_setup

Installing
-----------------

To install the library you can just run the following command:

.. code:: sh

    # In general
    pip install IPyC

    # Linux/macOS
    python3 -m pip install -U IPyC

    # Windows
    py -3 -m pip install -U IPyC

and can be used as follows:

.. code:: py

    import ipyc

To install the development version of the library directly from source:

.. code:: sh

    $ git clone https://github.com/dovedevic/IPyC.git
    $ cd IPyC
    $ python3 -m pip install -U .


Getting help
-------------

If you're having trouble with something, these resources might help.

- If you're looking for something specific, try the :ref:`index <genindex>` or :ref:`searching <search>`.
- Report bugs in the :resource:`issue tracker <issues>`.
- Check out examples in the :resource:`repository <examples>`.


Synchronous vs Asynchronous
----------------------------

IPyC comes in two favors: synchronous and asynchronous. Although the underlying mechanism which IPyC uses to communicate
is similar between flavors, the two differ in subtle ways. Each version has it's own library reference documentation, as
described in the table of contents.

Because the mechanism behind IPyC is the same, one can use a :class:`AsyncIPyCHost` host with a :class:`IPyCClient`
client and vice-versa.
