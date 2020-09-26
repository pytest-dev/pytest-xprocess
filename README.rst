pytest-xprocess
===============

.. image:: https://img.shields.io/pypi/v/pytest-xprocess.svg
    :target: https://pypi.org/project/pytest-xprocess

.. image:: https://img.shields.io/pypi/pyversions/pytest-xprocess.svg
    :target: https://pypi.org/project/pytest-xprocess

.. image:: https://github.com/pytest-dev/pytest-xprocess/workflows/build/badge.svg
  :target: https://github.com/pytest-dev/pytest-xprocess/actions


`pytest <https://docs.pytest.org/en/latest>`_ plugin for managing processes
across test runs.

Setting Up
----------

To use ``pytest-xprocess`` you just need to install it via::

    pip install pytest-xprocess

and that's all!

This will provide a ``xprocess`` fixture which can be used to ensure that
external processes on which your application depends are up and running during
testing. You can also use it to start and pre-configure test-specific databases
(i.e. Postgres, Couchdb).

Additionally, there are two new command line options::

     --xkill  # terminates all external processes
     --xshow  # shows currently running processes and log files


``xprocess`` fixture usage
-----------------------------

You typically define a project-specific fixture which
uses ``xprocess`` internally:

.. code-block:: python

    # content of conftest.py

    import pytest
    from xprocess import ProcessStarter

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            pattern = "PATTERN"
            args = ['command', 'arg1', 'arg2']

        logfile = xprocess.ensure("myserver", Starter)
        conn = # create a connection or url/port info to the server
        yield conn
        xprocess.getinfo("myserver").terminate() # clean up afterwards

The ``xprocess.ensure`` method takes the name of an external process and will
make sure it is running during your testing phase. Also, you are not restricted
to having a single external process at a time, ``xprocess`` can be used to handle
multiple diferent processes or several instances of the same process.

The ``Starter`` is a subclass that gets initialized with the working
directory created for this process.  If the server has not yet been
started:

- ``args`` are used to invoke a new subprocess.

- ``pattern`` is waited for in the logfile before returning.
  It should thus match a state of your server where it is ready to
  answer queries.

- ``env`` may be defined to customize the environment in which the
  new subprocess is invoked. To inherit the main test process
  environment, leave ``env`` set to the default (``None``).

- stdout is redirected to a logfile, which is returned pointing to the
  line right after the match

If the server is already running, simply the logfile is returned.

To customize the startup behavior, override other methods of the
ProcessStarter. For example, to extend the number of lines searched
for the startup info:

.. code-block:: python

    class Starter(ProcessStarter):
        pattern = 'process started at .*'
        args = ['command', 'arg1']

        def filter_lines(self, lines):
            return itertools.islice(lines, 500)

To override the wait behavior, override ``ProcessStarter.wait``.
See the ``xprocess.ProcessStarter`` interface for more details.

Note that the plugin needs to persist the process ID and logfile
information.  It does this in a sub directory of the directory
which contains a ``pytest.ini`` or ``setup.py`` file.
