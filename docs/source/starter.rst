.. _starter:


Starter Class
-------------

Your ``Starter`` will be used to customize how xprocess behaves. It must be a subclass of ``ProcessStarter`` where the required information to start a process instance will be provided.


Matching process output with ``pattern``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to detect that your process is ready to answer queries, ``pytest-xprocess`` allows the user to provide a string pattern by setting the class variable ``pattern`` in the Starter class. ``pattern`` will be waited for in the process logfile for a maximum time defined by ``timeout`` before timing out in case the provided pattern is not matched.

It's important to note that ``pattern`` is a regular expression and will be matched using python `re.search <https://docs.python.org/3/library/re.html#re.search>`_, so usual regex syntax (e.g. ``"eggs\s+([a-zA-Z_][a-zA-Z_0-9]*"``) can be used freely.

.. code-block:: python

    # content of conftest.py

    import pytest
    from xprocess import ProcessStarter

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

    # content of conftest.py

    import pytest
    from xprocess import ProcessStarter

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

    # content of conftest.py

    import pytest
    from xprocess import ProcessStarter

    @pytest.fixture
    def myserver(xprocess):
        class Starter(ProcessStarter):
            # will pass "$> myproc -name "bacon" -cores 4 <destdir>"  to the
            # subprocess.Popen constructor so the process can be started with
            # the given arguments
            args = ['myproc', '-name', '"bacon"', '-cores', 4, '<destdir>']

            # ...
