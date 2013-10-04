
import sys, subprocess
import py

server_path = py.path.local(__file__).dirpath("server.py")

pytest_plugins = "pytester"

def test_server(xprocess):
    xprocess.ensure("server", lambda cwd:
        ("started", [sys.executable, server_path, 5777]))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 5777))
    sock.sendall("hello\n".encode("utf8"))
    c = sock.recv(1)
    assert c == "1".encode("utf8")

def test_server2(xprocess):
    xprocess.ensure("server2", lambda cwd:
        ("started", [sys.executable, server_path, 5778]))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 5778))
    sock.sendall("world\n".encode("utf8"))
    c = sock.recv(1)
    assert c == "1".encode("utf8")

def test_shutdown(xprocess):
    xprocess.getinfo("server2").kill()
    xprocess.getinfo("server").kill()

def test_functional_work_flow(testdir):
    p = testdir.makepyfile("""
        import sys
        def test_server(request, xprocess):
            xprocess.ensure("server", lambda cwd:
                ("started", [sys.executable, %r, 5700]))
            import socket
            sock = socket.socket()
            sock.connect(("localhost", 5700))
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
