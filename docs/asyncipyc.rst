.. currentmodule:: ipyc


Asynchronous IPyC Reference
============================

The following outlines the async clients and their methods for async IPyC use.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See :ref:`logging_setup` for
    more information on how to set up and use the logging module with IPyC.


Async IPyC Host
----------------

.. autoclass:: AsyncIPyCHost
    :members:

Async IPyC Client
------------------

.. autoclass:: AsyncIPyCClient
    :members:

