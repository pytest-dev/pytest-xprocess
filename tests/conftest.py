import sys
from pathlib import Path

import pytest

from xprocess import ProcessStarter

pytest_plugins = "pytester"


@pytest.fixture
def xprocess_starter(xprocess, request):
    def _runner(
        start_pattern, proc_name, port, *test_args, read_lines=50, restart=False
    ):
        class Starter(ProcessStarter):
            pattern = start_pattern
            server_path = Path(__file__).parent.joinpath("server.py").absolute()
            max_read_lines = read_lines
            args = [sys.executable, server_path, port, *test_args]

        # return (pid, logfile)
        return xprocess.ensure(proc_name, Starter, restart)

    return _runner


@pytest.fixture
def xprocess_terminate(xprocess):
    def _terminator(name, **kwargs):
        proc = xprocess.getinfo(name)
        if proc.isrunning():
            print("terminating process {} (PID {})...\n".format(name, proc.pid))
            return proc.terminate(**kwargs)

    return _terminator


@pytest.fixture
def xprocess_info(xprocess):
    def _info(name):
        return xprocess.getinfo(name)

    return _info


class Test:

    HOST = "localhost"

    @pytest.fixture(autouse=True)
    def expose_starter(self, xprocess_starter):
        self.start_server = xprocess_starter

    @pytest.fixture(autouse=True)
    def expose_terminator(self, xprocess_terminate):
        self.terminate = xprocess_terminate

    @pytest.fixture(autouse=True)
    def expose_info(self, xprocess_info):
        self.get_info = xprocess_info
