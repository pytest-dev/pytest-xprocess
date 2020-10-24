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

    def test_ensure_not_restart(self):
        port = 6777
        proc_name = "server"
        pattern = "started"
        info = self.start_server(pattern, proc_name, port)
        assert self.start_server(pattern, proc_name, port, restart=False) == info
        self.terminate(proc_name)

    def test_startup_detection_max_read_lines(self):
        port = 6777
        data = "bacon\n"
        proc_name = "server"
        pattern = "finally started"
        self.start_server(pattern, proc_name, port, read_lines=62)
        self.request_response_cycle(port, data)
        self.terminate(proc_name)

    def test_runtime_error_on_start_fail(self):
        port = 6777
        pattern = "I will not be matched!"
        proc_name = "server"
        with pytest.raises(RuntimeError):
            self.start_server(
                pattern,
                proc_name,
                port,
                "--no-children",
                "--ignore-sigterm",
                restart=False,
            )
        # since we made xprocess fail to start the server on purpose, we cannot
        # terminate it using XProcessInfo.terminate method once it does not
        # know the PID, process name or even that it is running, so we tell the
        # server to terminate itself.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", port))
            sock.sendall(bytes("exit\n", "utf-8"))
