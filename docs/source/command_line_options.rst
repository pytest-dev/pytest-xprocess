.. _command_line_options:


Command Line Options
--------------------

Additionally to handling initialization, termination and logging of external process for you, ``pytest-xprocess`` also offers an easy way of manually managing long running processes that must persist across multiple test runs with ``--xshow`` and ``--xkill`` command line utilities.

Listing Long-running Processes with ``--xshow``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can query pytest-xprocess for the state and information of all previously started processes by invoking pytest command and passing the ``--xshow`` option::

    $ pytest --xshow

    10598 redis-server LIVE <path>/.pytest_cache/d/.xprocess/redis-server/xprocess.log
    10599 memcached DEAD <path>/.pytest_cache/d/.xprocess/memcached/xprocess.log
    10600 db-service LIVE <path>/pytest-xprocess/.pytest_cache/d/.xprocess/db-service/xprocess.log

As we can see, xprocess will list the state of all invoked processes along with some relevant information, namely: PID, process name, state (`ALIVE` or `DEAD`) and path to the process log file.


Terminating Long-running Processes with ``--xkill``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Besides quering for information on long-running processes, it's also possible to terminate any of these processes started by pytest-xprocess by invoking pytest command and passing ``--xkill`` option. Following is a simple example. Let's start by listing all processes::

    $ pytest --xshow

    10598 redis-server LIVE <path>/.pytest_cache/d/.xprocess/redis-server/xprocess.log
    10599 memcached LIVE <path>/.pytest_cache/d/.xprocess/memcached/xprocess.log
    10600 db-service LIVE <path>/pytest-xprocess/.pytest_cache/d/.xprocess/db-service/xprocess.log

Now, let's terminate the first one of PID 10598, redis-server::

    $ pytest --xkill redis-server

    10598 redis-server TERMINATED <path>/.pytest_cache/d/.xprocess/redis-server/xprocess.log

If we check the processes states again, we can see that redis-server is now ``DEAD``::

    $ pytest --xshow

    10598 redis-server DEAD <path>/.pytest_cache/d/.xprocess/redis-server/xprocess.log
    10599 memcached LIVE <path>/.pytest_cache/d/.xprocess/memcached/xprocess.log
    10600 db-service LIVE <path>/pytest-xprocess/.pytest_cache/d/.xprocess/db-service/xprocess.log

We call also kill all processes started by pytest-xprocess by only passing ``--xkill`` without a name::

    $ pytest --xkill # this will kill all processes
      ...
    $ pytest --xshow

    10598 redis-server DEAD <path>/.pytest_cache/d/.xprocess/redis-server/xprocess.log
    10599 memcached DEAD <path>/.pytest_cache/d/.xprocess/memcached/xprocess.log
    10600 db-service DEAD <path>/pytest-xprocess/.pytest_cache/d/.xprocess/db-service/xprocess.log
