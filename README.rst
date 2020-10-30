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
            # startup pattern
            pattern = "PATTERN"

            # command to start process
            args = ['command', 'arg1', 'arg2']

            # max startup waiting time
            # optional, defaults to 120 seconds
            timeout = 45

            # max lines read from stdout when matching pattern
            # optional, defaults to 100 lines
            max_read_lines = 100

        # ensure process is running and return its logfile
        logfile = xprocess.ensure("myserver", Starter)

        conn = # create a connection or url/port info to the server
        yield conn

        # clean up process and its children afterwards
        xprocess.getinfo("myserver").terminate()

The ``xprocess.ensure`` method takes the name of an external process and will
make sure it is running during your testing phase. Also, you are not restricted
to having a single external process at a time, ``xprocess`` can be used to handle
multiple diferent processes or several instances of the same process.

The ``Starter`` is a subclass that gets initialized with the working
directory created for this process.  If the server has not yet been
started:

- ``pattern`` is waited for in the logfile before returning.
  It should thus match a state of your server where it is ready to
  answer queries.

- ``args`` is a list of arguments, used to invoke a new subprocess.

- ``timeout`` may be used to specify the maximum time in seconds to wait for
  process startup.

- ``max_read_lines`` may be be used to extend the number of lines searched
  for ``pattern`` prior to considering the external process dead. By default,
  the first 50 lines of stdout are redirected to a logfile, which is returned
  pointing to the line right after the ``pattern`` match.

- Adicionally, ``env`` may be defined to customize the environment in which the
  new subprocess is invoked. To inherit the main test process
  environment, leave ``env`` set to the default (``None``).

If the server is already running, simply the logfile is returned.


Overriding Wait Behavior
------------------------

To override the wait behavior, override ``ProcessStarter.wait``.
See the ``xprocess.ProcessStarter`` interface for more details.

Note that the plugin uses a subdirectory in ``.pytest_cache`` to persist the
process ID and logfile information.


An Important Note Regarding Stream Buffering
--------------------------------------------

There have been reports of issues with test suites hanging when users attempt
to start external python processes with ``xprocess.ensure`` method. The reason
for this is that pytest-xprocess relies on matching predefined string patterns
written to your environment standard output streams to detect when processes
start and python's `sys.stdout/sys.stderr`_ buffering ends up getting in the
way of that. A possible solution for this problem is making both streams
unbuffered by passing the ``-u`` command-line option to your process start
command or setting the ``PYTHONUNBUFFERED`` environment variable.

.. _sys.stdout/sys.stderr: https://docs.python.org/3/library/sys.html#sys.stderr
