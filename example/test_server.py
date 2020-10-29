import os
import socket
import sys
import time

import psutil
import py
import pytest

from xprocess import ProcessStarter


server_path = py.path.local(__file__).dirpath("server.py")

pytest_plugins = "pytester"


def test_server(xprocess):
    pattern = "2 , % /.%,@%@._%%# #/%/ %\n"
    xprocess.ensure(
        "server", lambda cwd: (pattern, [sys.executable, server_path, 6777])
    )
    sock = socket.socket()
    sock.connect(("localhost", 6777))
    sock.sendall(b"hello\n")
    c = sock.recv(1)
    assert c == b"1"


def test_server2(xprocess):
    xprocess.ensure(
        "server2", lambda cwd: ("started", [sys.executable, server_path, 6778])
    )
    sock = socket.socket()
    sock.connect(("localhost", 6778))
    sock.sendall(b"world\n")
    c = sock.recv(1)
    assert c == b"1"


def test_server_env(xprocess):
    """Can return env as third item from preparefunc."""
    env = os.environ.copy()
    env["RESPONSE"] = "X"
    pattern = "4 , % /.%,@%@._%%# #/%/ %\n"
    xprocess.ensure(
        "server3",
        lambda cwd: (pattern, [sys.executable, server_path, 6779], env),
    )
    sock = socket.socket()
    sock.connect(("localhost", 6779))
    sock.sendall(b"hello\n")
    c = sock.recv(1)
    assert c == b"X"


def test_is_running(xprocess):
    assert xprocess.getinfo("server3").isrunning()
    assert xprocess.getinfo("server2").isrunning()
    assert xprocess.getinfo("server").isrunning()


def test_is_not_running_after_terminated_by_itself(server_info_for_terminated_server):
    server_info = server_info_for_terminated_server
    assert not server_info.isrunning()
    assert not server_info.isrunning(ignore_zombies=True)


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Zombie processes are not present on Windows"
)
def test_is_running_after_terminated_by_itself_when_not_ignoring_zombies(
    server_info_for_terminated_server,
):
    server_info = server_info_for_terminated_server
    assert not server_info.isrunning()
    assert server_info.isrunning(ignore_zombies=False)


def test_clean_shutdown(xprocess):
    proc_names = ["server", "server2", "server3"]
    all_children = [
        psutil.Process(xprocess.getinfo(name).pid).children() for name in proc_names
    ]
    children_pids = []
    for proc_children in all_children:
        assert len(proc_children) >= 1
        children_pids += [c.pid for c in proc_children]
    for name in proc_names:
        xprocess.getinfo(name).terminate()
    for pid in children_pids:
        assert not psutil.pid_exists(pid)
    for name in proc_names:
        assert not xprocess.getinfo(name).isrunning()


def test_is_not_running_after_termination(xprocess):
    assert not xprocess.getinfo("server3").isrunning()
    assert not xprocess.getinfo("server2").isrunning()
    assert not xprocess.getinfo("server").isrunning()


def test_functional_work_flow(testdir):
    testdir.makepyfile(
        """
        import sys
        def test_server(request, xprocess):
            xprocess.ensure("server", lambda cwd:
                ("started", [sys.executable, %r, 6700]))
            import socket
            sock = socket.socket()
            sock.connect(("localhost", 6700))
            sock.sendall("world\\n".encode("utf8"))
            c = sock.recv(1)
            assert c == "1".encode("utf8")
    """
        % str(server_path)
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines("*1 passed*")
    result = testdir.runpytest("--xshow")
    result.stdout.fnmatch_lines("*LIVE*")
    result = testdir.runpytest("--xkill")
    result.stdout.fnmatch_lines("*TERMINATED*")


@pytest.fixture(scope="module")
def server_info_for_terminated_server(xprocess):
    server_name = "server4"
    server_port = 6780

    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, server_port, "--no-children"]

    xprocess.ensure(server_name, Starter)
    sock = socket.socket()
    sock.connect(("localhost", server_port))
    try:
        for _ in range(50):
            sock.sendall(b"kill\n")
            sock.recv(1)
            time.sleep(0.1)
    except (
        BrokenPipeError,
        ConnectionAbortedError,
        ConnectionResetError,
    ):  # Server is terminated
        server_info = xprocess.getinfo(server_name)
        yield server_info
    server_info.terminate()


def test_startup_detection_max_read_lines(xprocess):
    class Starter(ProcessStarter):
        pattern = "finally started"
        args = [sys.executable, server_path, 6777]
        max_read_lines = 200

    xprocess.ensure("server", Starter)
    sock = socket.socket()
    sock.connect(("localhost", 6777))
    sock.sendall(b"hello\n")
    c = sock.recv(1)
    assert c == b"1"
    xprocess.getinfo("server").terminate()


def test_timeout(xprocess):
    class Starter(ProcessStarter):
        pattern = "will not match"
        args = [sys.executable, server_path, 6777, "--no-children"]
        max_read_lines = 500
        timeout = 2

    with pytest.raises(TimeoutError):
        xprocess.ensure("server", Starter)
    # kill hanging server instance
    sock = socket.socket()
    sock.connect(("localhost", 6777))
    try:
        for _ in range(10):
            sock.sendall(b"kill\n")
            sock.recv(1)
            time.sleep(0.1)
    except (
        BrokenPipeError,
        ConnectionAbortedError,
        ConnectionResetError,
    ):  # Server is terminated
        pass
