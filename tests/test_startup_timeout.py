import socket
import sys
import time
from pathlib import Path

import pytest

from xprocess import ProcessStarter

server_path = Path(__file__).parent.joinpath("server.py").absolute()


def cleanup_server_instance(tcp_port):
    sock = socket.socket()
    sock.connect(("localhost", tcp_port))
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


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_timeout_raise_exception(tcp_port, proc_name, xprocess, request):
    class Starter(ProcessStarter):
        timeout = 2
        max_read_lines = 500
        pattern = "will not match"
        args = [sys.executable, server_path, tcp_port, "--no-children"]

    with pytest.raises(TimeoutError):
        xprocess.ensure(proc_name, Starter)
    cleanup_server_instance(tcp_port)
