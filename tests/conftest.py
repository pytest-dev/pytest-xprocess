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
