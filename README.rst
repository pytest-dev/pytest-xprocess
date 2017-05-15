.. image:: https://drone.io/bitbucket.org/pytest-dev/pytest-xprocess/status.png
   :target: https://drone.io/bitbucket.org/pytest-dev/pytest-xprocess/latest
.. image:: https://pypip.in/v/pytest-xprocess/badge.png
   :target: https://pypi.python.org/pypi/pytest-xprocess

experimental py.test plugin for managing processes across test runs
===================================================================

Usage
---------

install via::

    pip install pytest-xprocess

This will provide a ``xprocess`` fixture which helps
you to ensure that one ore more longer-running processes
are present for your tests.  You can use it to start and
pre-configure test-specific databases (Postgres, Couchdb, ...).

Additionally there are two new command line options::

     --xkill  # kills all external processes
     --xshow  # shows currently running processes and log files


``xprocess`` fixture usage
-----------------------------

You typically define a project-specific fixture which
uses the ``xprocess`` fixture internally::

    # content of conftest.py

    import pytest

    @pytest.fixture
    def myserver(xprocess):
        def preparefunc(cwd):
            return ("PATTERN", [subprocess args])

        logfile = xprocess.ensure("myserver", preparefunc)
        conn = # create a connection or url/port info to the server
        return conn

The ``xprocess.ensure`` function takes a name for the external process
because you can have multiple external processes.

The ``preparefunc`` is a function which gets the current working directory and
returns a ``(PATTERN, args, env)`` tuple.  If the server has not yet been
started:

- the returned ``args`` are used to perform a subprocess invocation with
  environment ``env`` (a mapping) and redirect its stdout to a new logfile

- the ``PATTERN`` is waited for in the logfile before returning.
  It should thus match a state of your server where it is ready to
  answer queries.

- the logfile is returned pointing to the line right after the match

else, if the server is already running simply the logfile is returned.

To inherit the main test process environment, return ``None`` for ``env``, or
omit it and return just ``(PATTERN, args)`` from the ``preparefunc``.

Note that the plugin needs to persist the process ID and logfile
information.  It does this in a sub directory of the directory
which contains a ``pytest.ini`` or ``setup.py`` file.


Notes
-------------

The repository of this plugin is at http://bitbucket.org/pytest-dev/pytest-xprocess

For more info on py.test see http://pytest.org
