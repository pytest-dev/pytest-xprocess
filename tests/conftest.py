import sys
from pathlib import Path

import pytest

from xprocess import ProcessStarter


@pytest.fixture
def test_server(xprocess):
    python_executable = sys.executable

    class Starter(ProcessStarter):
        pattern = "started"
        server_path = Path(__file__).parent.joinpath("server.py").absolute()
        args = [python_executable, server_path, "-u"]

    xprocess.ensure("test_server", Starter)
    yield
    xprocess.getinfo("test_server").terminate()
