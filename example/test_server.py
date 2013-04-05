
import sys, subprocess
import py

server_path = py.path.local(__file__).dirpath("server.py")

def test_server(xprocess):
    xprocess.ensure("server", lambda cwd:
        ("started", [sys.executable, server_path, 5777]))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 5777))
    sock.sendall("hello\n")
    c = sock.recv(1)
    assert c == "1"

def test_server2(xprocess):
    xprocess.ensure("server2", lambda cwd:
        ("started", [sys.executable, server_path, 5778]))
    import socket
    sock = socket.socket()
    sock.connect(("localhost", 5778))
    sock.sendall("world\n")
    c = sock.recv(1)
    assert c == "1"
