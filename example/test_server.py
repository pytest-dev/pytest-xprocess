import os
import sys

import psutil
import py


server_path = py.path.local(__file__).dirpath("server.py")

pytest_plugins = "pytester"


def test_server(xprocess):
    pattern = "2 , % /.%,@%@._%%# #/%/ %\n"
    xprocess.ensure(
        "server", lambda cwd: (pattern, [sys.executable, server_path, 6777])
    )
    import socket

    sock = socket.socket()
    sock.connect(("localhost", 6777))
    sock.sendall(b"hello\n")
    c = sock.recv(1)
    assert c == b"1"


def test_server2(xprocess):
    xprocess.ensure(
        "server2", lambda cwd: ("started", [sys.executable, server_path, 6778])
    )
    import socket

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
    import socket

    sock = socket.socket()
    sock.connect(("localhost", 6779))
    sock.sendall(b"hello\n")
    c = sock.recv(1)
    assert c == b"X"


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
