import os
import sys

import py


server_path = py.path.local(__file__).dirpath("server.py")

pytest_plugins = "pytester"


def test_server(xprocess):
    xprocess.ensure("server", lambda cwd:
        ("started", [sys.executable, server_path, 6777]))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 6777))
    sock.sendall("hello\n".encode("utf8"))
    c = sock.recv(1)
    assert c == "1".encode("utf8")


def test_server2(xprocess):
    xprocess.ensure("server2", lambda cwd:
        ("started", [sys.executable, server_path, 6778]))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 6778))
    sock.sendall("world\n".encode("utf8"))
    c = sock.recv(1)
    assert c == "1".encode("utf8")


def test_server_env(xprocess):
    """Can return env as third item from preparefunc."""
    env = os.environ.copy()
    env['RESPONSE'] = 'X'
    xprocess.ensure("server3", lambda cwd:
                    ("started", [sys.executable, server_path, 6779], env))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 6779))
    sock.sendall("hello\n".encode("utf8"))
    c = sock.recv(1)
    assert c == "X".encode("utf8")


def test_shutdown(xprocess):
    xprocess.getinfo("server3").terminate()
    xprocess.getinfo("server2").terminate()
    xprocess.getinfo("server").terminate()


def test_shutdown_legacy(xprocess):
    """
    Ensure XProcessInfo.kill() is still supported, if deprecated.
    """
    def runner(cwd):
        wait_pattern = 'started'
        args = sys.executable, server_path, 6780
        return wait_pattern, args

    xprocess.ensure("server4", runner)
    xprocess.getinfo('server4').kill()


def test_functional_work_flow(testdir):
    testdir.makepyfile("""
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
    """ % str(server_path))
    result = testdir.runpytest()
    result.stdout.fnmatch_lines("*1 passed*")
    result = testdir.runpytest("--xs")
    result.stdout.fnmatch_lines("*LIVE*")
    result = testdir.runpytest("--xk")
    result.stdout.fnmatch_lines("*TERMINATED*")
