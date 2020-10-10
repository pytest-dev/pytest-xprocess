import socket
import sys
from abc import ABC
from abc import abstractmethod
from pathlib import Path

import pytest

from xprocess import ProcessStarter

pytest_plugins = "pytester"


@pytest.fixture
def make_runner(xprocess, request):
    def _runner(start_pattern, proc_name, port):
        class Starter(ProcessStarter):
            pattern = start_pattern
            server_path = Path(__file__).parent.joinpath("server.py").absolute()
            args = [sys.executable, "-u", server_path, port]

        logfile = xprocess.ensure(proc_name, Starter)
        return logfile

    return _runner


@pytest.fixture
def make_terminator(xprocess):
    def _terminator(name):
        proc = xprocess.getinfo(name)
        if proc.isrunning():
            print(f"process {name} (PID {proc.pid}), running, terminating...\n")
            proc.terminate()

    return _terminator


class BaseTests(ABC):

    HOST = "localhost"

    @property
    def port(self):
        raise NotImplementedError

    @port.setter
    @abstractmethod
    def port(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @data.setter
    @abstractmethod
    def data(self):
        raise NotImplementedError

    @pytest.fixture(autouse=True)
    def get_server(self, make_runner):
        self._serve = make_runner

    @pytest.fixture(autouse=True)
    def get_terminator(self, make_terminator):
        self._terminator = make_terminator

    def test_request_response(self):
        print("running test_base_class...")
        self._serve("2 , % /.%,@%@._%%# #/%/ %\n", "server", 6777)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.HOST, self.port))
            sock.sendall(bytes(self.data, "utf-8"))
            received = str(sock.recv(1024), "utf-8")
            assert received == self.data.upper()
        self._terminator("server")
