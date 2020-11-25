pytest-xprocess
===============

.. image:: https://img.shields.io/maintenance/yes/2020?color=blue
    :target: https://github.com/pytest-dev/pytest-xprocess
    :alt: Maintenance

.. image:: https://img.shields.io/github/last-commit/pytest-dev/pytest-xprocess?color=blue
    :target: https://github.com/pytest-dev/pytest-xprocess/commits/master
    :alt: GitHub last commit

.. image:: https://img.shields.io/github/issues-pr-closed-raw/pytest-dev/pytest-xprocess?color=blue
    :target: https://github.com/pytest-dev/pytest-xprocess/pulls?q=is%3Apr+is%3Aclosed
    :alt: GitHub closed pull requests

.. image:: https://img.shields.io/github/issues-closed/pytest-dev/pytest-xprocess?color=blue
    :target: https://github.com/pytest-dev/pytest-xprocess/issues?q=is%3Aissue+is%3Aclosed
    :alt: GitHub closed issues

.. image:: https://img.shields.io/pypi/dm/pytest-xprocess?color=blue
    :target: https://pypi.org/project/pytest-xprocess/
    :alt: PyPI - Downloads

.. image:: https://img.shields.io/github/languages/code-size/pytest-dev/pytest-xprocess?color=blue
    :target: https://github.com/pytest-dev/pytest-xprocess
    :alt: Code size

.. image:: https://img.shields.io/pypi/v/pytest-xprocess.svg?color=blue
  :target: https://github.com/pytest-dev/pytest-xprocess/releases
  :alt: Release

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?color=blue
   :target: https://github.com/pytest-dev/pytest-xprocess/blob/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pytest-xprocess.svg?color=blue
    :target: https://pypi.org/project/pytest-xprocess
    :alt: supported python versions

.. image:: https://img.shields.io/github/issues-raw/pytest-dev/pytest-xprocess.svg?color=blue
   :target: https://github.com/pytest-dev/pytest-xprocess/issues
   :alt: Issues

.. image:: https://github.com/pytest-dev/pytest-xprocess/workflows/build/badge.svg
  :target: https://github.com/pytest-dev/pytest-xprocess/actions
  :alt: build status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: style


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
--------------------------

You typically define a project-specific fixture which uses ``xprocess``
internally. Following are two examples:

**Minimal reference fixture**

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

        # ensure process is running and return its logfile
        logfile = xprocess.ensure("myserver", Starter)

        conn = # create a connection or url/port info to the server
        yield conn

        # clean up whole process tree afterwards
        xprocess.getinfo("myserver").terminate()

**Complete reference fixture**

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
            # optional, defaults to 50 lines
            max_read_lines = 100

            def startup_check(self):
                """
                Optional callback used to check process responsiveness
                after the provided pattern has been matched. Returned
                value must be a boolean, where:

                True: Process has been sucessfuly started and is ready
                      to answer queries.

                False: Callback failed during process startup.

                This method will be called multiple times to check if the
                process is ready to answer queries. A 'TimeoutError' exception
                will be raised if the provied 'startup_check' does not
                return 'True' before 'timeout' seconds.
                """
                sock = socket.socket()
                sock.connect(("localhost", 6777))
                sock.sendall(b"testing connection\n")
                return sock.recv(1) == "connection ok!"

        # ensure process is running and return its logfile
        logfile = xprocess.ensure("myserver", Starter)

        conn = # create a connection or url/port info to the server
        yield conn

        # clean up whole process tree afterwards
        xprocess.getinfo("myserver").terminate()

The ``xprocess.ensure`` method takes the name of an external process and will
make sure it is running during your testing phase. Also, you are not restricted
to having a single external process at a time, ``xprocess`` can be used to handle
multiple diferent processes or several instances of the same process.


Starter Class
-------------

Your ``Starter`` must be a subclass of ``ProcessStarter`` where the required
information to start a process instance will be provided:

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

- ``startup_check`` when provided will be called upon to check process
  responsiveness after ``ProcessStarter.pattern`` is matched. By default,
  ``XProcess.ensure`` will attempt to match ``ProcessStarter.pattern`` when
  starting a process, if matched, xprocess will consider the process as ready
  to answer queries. If ``startup_check`` is provided though, its return
  value will also be considered to determine if the process has been
  properly started. If ``startup_check`` returns True after
  ``ProcessStarter.pattern`` has been matched, ``XProcess.ensure`` will return
  sucessfully. In contrast, if ``startup_check`` does not return ``True``
  before timing out, ``XProcess.ensure`` will raise a ``TimeoutError`` exception.

- Adicionally, ``env`` may be defined to customize the environment in which the
  new subprocess is invoked. To inherit the main test process
  environment, leave ``env`` set to the default (``None``).

If the process is already running, simply the logfile is returned.


Overriding Wait Behavior
------------------------

To override the wait behavior, override ``ProcessStarter.wait``. See the
``xprocess.ProcessStarter`` interface for more details. Note that the
plugin uses a subdirectory in ``.pytest_cache`` to persist the process ID
and logfile information.


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
