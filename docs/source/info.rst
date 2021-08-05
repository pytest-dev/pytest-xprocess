.. _info:


Info Object
-----------

All information related to a process started with pytest-xprocess is exposed through the ``ProcessInfo`` object. An instance of this object for a given process can be obtained by using the method ``XProcess.getinfo`` as shown in the following example.

.. code-block:: python

    import pytest
    from xprocess import ProcessStarter

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
        # ...

        # clean up whole process tree afterwards
        process_info = xprocess.getinfo("my_process_name")


Terminating Processes and Process Trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A process or process tree started by xprocess can be recursively terminated by using ``XProcessInfo.terminate``. This method takes two optional keyword arguments:

- ``timeout``: Maximum time in seconds to wait on process termination.When timeout is reached after sending SIGTERM, this method will attempt to SIGKILL the process and return ``-1`` in case the operation times out again (defaults to 20 seconds).

- ``kill_proc_tree``: Enable/disable recursive process tree termination. Defaults to True.

Regarding termination behaviour, xprocess will Attempt graceful termination starting by leaves of a process tree and work its way towards the root process. For example, if we have:

::

     A ─┐
        │
        ├─ B (child) ─┐
        │             └─ X (grandchild) ─┐
        │                                └─ Y (great grandchild)
        ├─ C (child)
        └─ D (child)

The termination order will be: D, C, Y, X, B and finally A.

As stated, it will first attempt graceful termination with SIGTERM followed by abrupt SIGKILL in case the first signal fails.


Checking a Process Status
~~~~~~~~~~~~~~~~~~~~~~~~~

``XProcessInfo.isrunning`` can be used to verify the current status of a started process during a test
run. This method takes a single optional keyword argument:

- ``ignore_zombies``: Sometimes a process that terminates itself during test execution or children of a crashed process will become a zombie process. This flag can be set to ``True`` or ``False`` if the user wants to ignore zombies or not.

.. code-block:: python

    def test_my_feature(my_fixture):
        if my_fixture.geinfo("my_proc").isrunning():
            # your process is running!
            # do things with it...
        else:
            # your process is not running!
