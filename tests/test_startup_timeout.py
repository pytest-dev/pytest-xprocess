import socket
import time

import pytest
from conftest import Test


class TestStartupTimeout(Test):
    """test timeout functionality when starting processes"""

    def cleanup_server_instance(self, port):
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

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")]
    )
    def test_timeout_raise_exception(self, port, proc_name):
        with pytest.raises(TimeoutError):
            self.start_server(
                "will not match",
                proc_name,
                port,
                "--no-children",
                read_lines=500,
                start_timeout=1,
            )
        self.cleanup_server_instance(port)
