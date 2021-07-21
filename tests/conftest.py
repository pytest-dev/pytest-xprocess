import socket
from contextlib import closing

import pytest

from xprocess import ProcessStarter

pytest_plugins = "pytester"


@pytest.fixture
def example(xprocess):
    """fixture for testing ResourceWarnings
    in test_resource_cleanup.py module"""

    class Starter(ProcessStarter):
        pattern = "foo"
        args = ("sh", "-c", "echo foo; sleep 10; echo bar")

    xprocess.ensure("example", Starter)
    yield
    xprocess.getinfo("example").terminate()


@pytest.fixture
def tcp_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
