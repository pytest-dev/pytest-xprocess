Experimental `py.test <https://pytest.org>`_ plugin for managing processes
across test runs.

Usage
---------

install via::

    pip install pytest-xprocess

This will provide a ``xprocess`` fixture which helps
you to ensure that one ore more longer-running processes
are present for your tests.  You can use it to start and
pre-configure test-specific databases (Postgres, Couchdb, ...).

Additionally there are two new command line options::

     --xkill  # terminates all external processes
     --xshow  # shows currently running processes and log files


``xprocess`` fixture usage
-----------------------------

You typically define a project-specific fixture which
uses the ``xprocess`` fixture internally::

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
        return conn

The ``xprocess.ensure`` function takes a name for the external process
because you can have multiple external processes.

The ``Starter`` is a subclass that gets initialized with the working
directory created for this process.  If the server has not yet been
started:

- the ``args`` are used to invoke a new subprocess.

- the ``pattern`` is waited for in the logfile before returning.
  It should thus match a state of your server where it is ready to
  answer queries.

- ``env`` may be defined to customize the environment in which the
  new subprocess is invoked. To inherit the main test process
  environment, leave ``env`` set to the default (``None``).

- stdout is redirected to a logfile, which is returned pointing to the
  line right after the match

else, if the server is already running simply the logfile is returned.

To customize the startup behavior, override other methods of the
ProcessStarter. For example, to extend the number of lines searched
for the startup info:

    class Starter(ProcessStarter):
        pattern = 'process started at .*'
        args = ['command', 'arg1']

        def filter_lines(self, lines):
            return itertools.islice(lines, 500)

To override the wait behavior, override :method:`ProcessStarter.wait`.
See the :class:`xprocess.ProcessStarter` interface for more details.

Note that the plugin needs to persist the process ID and logfile
information.  It does this in a sub directory of the directory
which contains a ``pytest.ini`` or ``setup.py`` file.
