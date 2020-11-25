import socket
import sys
from pathlib import Path

import pytest

from xprocess import ProcessStarter

server_path = Path(__file__).parent.joinpath("server.py").absolute()


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_callback_success(xprocess, port, proc_name):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, port, "--no-children"]

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("localhost", port))
                sock.sendall(bytes("bacon\n", "utf-8"))
                received = str(sock.recv(1024), "utf-8")
                return received == "bacon\n".upper()

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.isrunning()
    info.terminate()


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_callback_fail(xprocess, port, proc_name):
    class Starter(ProcessStarter):
        timeout = 5
        pattern = "started"
        args = [sys.executable, server_path, port, "--no-children"]

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("localhost", port))
                sock.sendall(bytes("bacon\n", "utf-8"))
                received = str(sock.recv(1024), "utf-8")
                return received == "wrong"  # this wont match

    with pytest.raises(TimeoutError):
        xprocess.ensure(proc_name, Starter)
    xprocess.getinfo(proc_name).terminate()
