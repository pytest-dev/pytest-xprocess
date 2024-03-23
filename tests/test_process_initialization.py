import socket
import sys
from pathlib import Path

import pytest

from xprocess import ProcessStarter

server_path = Path(__file__).parent.joinpath("server.py").absolute()


def request_response_cycle(tcp_port, data):
    """test started server instance by sending
    request and checking response"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", tcp_port))
        sock.sendall(bytes(data, "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        return received == data.upper()


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_servers_start(tcp_port, proc_name, xprocess):
    data = "bacon\n"

    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port, "--no-children"]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert request_response_cycle(tcp_port, data)
    assert info.isrunning()
    info.terminate()


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_ensure_not_restart(tcp_port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port, "--no-children"]

    proc_id = xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert xprocess.ensure(proc_name, Starter) == proc_id
    assert info.isrunning()
    info.terminate()


@pytest.mark.parametrize(
    "proc_name,proc_pttrn,lines",
    [
        ("s1", "started", 21),
        ("s2", "spam, bacon, eggs", 30),
        ("s3", "finally started", 130),
    ],
)
def test_startup_detection_max_read_lines(
    tcp_port, proc_name, proc_pttrn, lines, xprocess
):
    data = "bacon\n"

    class Starter(ProcessStarter):
        pattern = proc_pttrn
        max_read_lines = lines
        args = [sys.executable, server_path, tcp_port, "--no-children"]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.isrunning()
    assert request_response_cycle(tcp_port, data)
    info.terminate()


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_runtime_error_on_start_fail(tcp_port, proc_name, xprocess):
    restart = False

    class Starter(ProcessStarter):
        pattern = "I will not be matched!"
        args = [
            sys.executable,
            server_path,
            tcp_port,
            "--no-children",
            "--ignore-sigterm",
        ]

    with pytest.raises(RuntimeError):
        xprocess.ensure(proc_name, Starter, restart)

    # since we made xprocess fail to start the server on purpose, we cannot
    # terminate it using XProcessInfo.terminate method once it does not
    # know the PID, process name or even that it is running, so we tell the
    # server to terminate itself.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", tcp_port))
        sock.sendall(bytes("exit\n", "utf-8"))


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_popen_kwargs(tcp_port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port, "--no-children"]
        popen_kwargs = {"universal_newlines": True}

    xprocess.ensure(proc_name, Starter)

    info = xprocess.getinfo(proc_name)
    proc = xprocess.resources[-1].popen

    text_mode = proc.text_mode

    assert info.isrunning()
    assert text_mode

    info.terminate()


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_startup_without_pattern(tcp_port, proc_name, xprocess):
    data = "bacon\n"

    class Starter(ProcessStarter):
        args = [sys.executable, server_path, tcp_port, "--no-children"]

        def startup_check(self):
            return request_response_cycle(tcp_port, data)

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.isrunning()
    info.terminate()


@pytest.mark.parametrize(
    "proc_name,proc_pttrn,lines",
    [
        ("s1", "will not match", 21),
        ("s2", "spam, bacon, eggs", 30),
        ("s3", "finally started", 130),
    ],
)
def test_startup_with_pattern_and_callback(
    tcp_port, proc_name, proc_pttrn, lines, xprocess
):
    data = "bacon\n"

    class Starter(ProcessStarter):
        pattern = proc_pttrn
        max_read_lines = lines
        args = [sys.executable, server_path, tcp_port, "--no-children"]

        def startup_check(self):
            return request_response_cycle(tcp_port, data)

    if proc_name == "s1":
        with pytest.raises(RuntimeError):
            xprocess.ensure(proc_name, Starter)
        # since we made xprocess fail to start the server on purpose, we cannot
        # terminate it using XProcessInfo.terminate method once it does not
        # know the PID, process name or even that it is running, so we tell the
        # server to terminate itself.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", tcp_port))
            sock.sendall(bytes("exit\n", "utf-8"))
    else:
        xprocess.ensure(proc_name, Starter)
        info = xprocess.getinfo(proc_name)
        assert info.isrunning()
        assert request_response_cycle(tcp_port, data)
        info.terminate()
