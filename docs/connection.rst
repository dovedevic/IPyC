.. currentmodule:: ipyc


IPyC Communication Reference
=============================

The following outlines how communication links are established and their use.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See :ref:`logging_setup` for
    more information on how to set up and use the logging module with IPyC.


Synchronous IPyC Link
----------------------

.. autoclass:: IPyCLink
    :members:

Asynchronous IPyC Link
-----------------------

.. autoclass:: AsyncIPyCLink
    :members:

