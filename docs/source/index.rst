.. pytest-xprocess documentation master file, created by
   sphinx-quickstart on Sun Jun  6 00:00:19 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pytest-xprocess's documentation!
===========================================

A `pytest <http://pytest.org>`_ plugin for managing processes. It will make sure external processes on which your application depends are up during every pytest run without the need of manual start-up.


Quickstart
----------

Install plugin via ``pip``::

    $ pip install pytest-xprocess

Define your process fixture in ``conftest.py``:

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

Now you can use this fixture in any test functions where ``myserver`` needs to
be up and ``xprocess`` will take care of it for you!

.. toctree::
   :maxdepth: 2

   starter
   command_line_options
   contributing
   changes
   contact
