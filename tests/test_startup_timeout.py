import socket
import sys
import time
from pathlib import Path

import pytest

from xprocess import ProcessStarter

server_path = Path(__file__).parent.joinpath("server.py").absolute()


def cleanup_server_instance(port):
    sock = socket.socket()
    sock.connect(("localhost", port))
    try:
        for _ in range(10):
            sock.sendall(b"exit\n")
            sock.recv(1)
            time.sleep(0.1)
    except (
        BrokenPipeError,
        ConnectionAbortedError,
        ConnectionResetError,
    ):  # Server is terminated
        pass
    sock.close()


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_timeout_raise_exception(port, proc_name, xprocess, request):
    class Starter(ProcessStarter):
        timeout = 2
        max_read_lines = 500
        pattern = "will not match"
        args = [sys.executable, server_path, port, "--no-children"]

    with pytest.raises(TimeoutError):
        xprocess.ensure(proc_name, Starter)
    cleanup_server_instance(port)
