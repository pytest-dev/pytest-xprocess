.. _starter:


Starter Class
-------------

Your ``Starter`` will be used to customize how xprocess behaves. It must be a subclass of ``ProcessStarter`` where the required information to start a process instance will be provided.


Matching process output with ``pattern``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to detect that your process is ready to answer queries, ``pytest-xprocess`` allows the user to provide a string pattern by setting the class variable ``pattern`` in the Starter class. ``pattern`` will be waited for in the process logfile for a maximum time defined by ``timeout`` before timing out in case the provided pattern is not matched.

It's important to note that ``pattern`` is a regular expression and will be matched using python `re.search <https://docs.python.org/3/library/re.html#re.search>`_, so usual regex syntax (e.g. ``"eggs\s+([a-zA-Z_][a-zA-Z_0-9]*"``) can be used freely.

.. code-block:: python

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # Here, we assume that our hypothetical process
            # will print the message "server has started"
            # once initialization is done
            pattern = "[Ss]erver has started!"

            # ...


Controlling Startup Wait Time with ``timeout``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some processes naturally take longer to start than others. By default, ``pytest-xprocess`` will wait for a maxium of 120 seconds for a given process to start before raising a ``TimeoutError``. Changing this value may be useful, for example, when the user knows that a given process would never take longer than a known amount of time to start under normal circunstances, so if it does go over this known upper boundary, that means something is wrong and the waiting process must be interrupted. The maxium wait time can be controlled thourgh the class variable ``timeout``.

.. code-block:: python

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # will wait for 10 seconds before timing out
            timeout = 10

            # ...


Telling pytest-xprocess how to start a process with ``args``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to start a process, pytest-xprocess must be given a command to be passed into the `subprocess.Popen constructor <https://docs.python.org/3/library/subprocess.html#popen-constructor>`_. Any arguments passed to the process command can also be passed using ``args``. As an example, if I usually use the following command to start a given process:

``$> myproc -name "bacon" -cores 4 <destdir>``

That would look like:

``args = ['myproc', '-name', '"bacon"', '-cores', 4, '<destdir>']``

when using ``args`` in  ``pytest-xprocess`` to start the same process.

.. code-block:: python

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # will pass "$> myproc -name "bacon" -cores 4 <destdir>"  to the
            # subprocess.Popen constructor so the process can be started with
            # the given arguments
            args = ['myproc', '-name', '"bacon"', '-cores', 4, '<destdir>']

            # ...


Limiting number of lines searched for pattern with ``max_read_lines``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the specified string ``patern`` can be found within the first ``n`` outputted lines, there's no reason to search all the remaining output (possibly hundreds of lines or more depending on the process). For that reason, ``pytest-xprocess`` allows the user to limit the maxium number of lines outputted by the process that will be searched for the given pattern with ``max_read_lines``.

If ``max_read_lines`` lines have been searched and ``patern`` has not been found, a ``RuntimeError`` will be raised to let the user know that startup has failed.

When not specified, ``max_read_lines`` will default to 50 lines.

.. code-block:: python

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # search the first 12 lines for pattern, if not found
            # a RuntimeError will be raised informing the user
            max_read_lines = 12

            # ...

Making sure your process is ready with ``startup_check``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some processes don't have that much console output, so ``pytest-xprocess`` offers a way to double-check that the initialized process is in a query-ready state by allowing the user to define a  callback function ``startup_check``.

When provided, this function  will be called upon to check process responsiveness after ``ProcessStarter.pattern`` has been matched.

By default, ``XProcess.ensure`` will attempt to match ``ProcessStarter.pattern`` when starting a process, if matched, xprocess will consider the process as ready to answer queries. If ``startup_check`` is provided though, its return value will also be considered to determine if the process has been properly started. If ``startup_check`` returns True after ``ProcessStarter.pattern`` has been matched, ``XProcess.ensure`` will return sucessfully. In contrast, if ``startup_check`` does not return ``True`` before timing out, ``XProcess.ensure`` will raise a ``TimeoutError`` exception.

``startup_check`` must return a boolean value (``True`` or ``False``)

.. code-block:: python

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # checks if our server is ready with a ping
            def startup_check(self):
                sock = socket.socket()
                sock.connect(("myhostname", 6777))
                sock.sendall(b"ping\n")
                return sock.recv(1) == "pong!"
            # ...


Customizing process execution environment with ``env``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the execution environment of the main test process will be inherited by the invoked process. But, if desired, it's possible to customize the environment in which the new process will be invoked by providing a mapping containg the desired environment variables and their respective values with ``env``.

.. code-block:: python

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # checks if our server is ready with a ping
            env = {"PYTHONPATH": str(some_path), "PYTHONUNBUFFERED": "1"}

            # ...


Overriding Wait Behavior
~~~~~~~~~~~~~~~~~~~~~~~~

To override the wait behavior, override ``ProcessStarter.wait``. See the
``xprocess.ProcessStarter`` interface for more details. Note that the
plugin uses a subdirectory in ``.pytest_cache`` to persist the process ID
and logfile information.


An Important Note Regarding Stream Buffering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There have been reports of issues with test suites hanging when users attempt to start external **python** processes with ``xprocess.ensure`` method. The reason for this is that ``pytest-xprocess`` relies on matching predefined string patterns written to your environment standard output streams to detect when processes start and python's `sys.stdout/sys.stderr`_ buffering ends up getting in the way of that.

A possible solution for this problem is making both streams unbuffered by passing the ``-u`` command-line option to your process start command or setting the ``PYTHONUNBUFFERED`` environment variable.

.. _sys.stdout/sys.stderr: https://docs.python.org/3/library/sys.html#sys.stderr
