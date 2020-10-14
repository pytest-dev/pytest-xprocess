import socket

import pytest
from conftest import Test


class TestProcessInitialization(Test):
    """test initialization of multiple server instances"""

    def request_response_cycle(self, port, data):
        """test started server instance by sending
        request and checking response"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", port))
            sock.sendall(bytes(data, "utf-8"))
            received = str(sock.recv(1024), "utf-8")
            assert received == data.upper()

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3"), (6780, "s4")]
    )
    def test_servers_start(self, port, proc_name):
        data = "bacon\n"
        pattern = "started"
        self.start_server(pattern, proc_name, port)
        self.request_response_cycle(port, data)
        assert self.terminate(proc_name)
