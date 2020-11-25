from pathlib import Path


def test_functional_work_flow(testdir):
    server_path = Path(__file__).parent.joinpath("server.py").absolute()
    testdir.makepyfile(
        """
        import sys
        import socket
        from xprocess import ProcessStarter

        def test_server(request, xprocess):
            port = 6776
            data = "spam\\n"
            server_path = %r

            class Starter(ProcessStarter):
                pattern = "started"
                max_read_lines = 200
                args = [sys.executable, server_path, port]

            xprocess.ensure("server", Starter)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("localhost", port))
                sock.sendall(bytes(data, "utf-8"))
                received = str(sock.recv(1024), "utf-8")
                assert received == data.upper()
    """
        % str(server_path)
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines("*1 passed*")
    result = testdir.runpytest("--xshow")
    result.stdout.fnmatch_lines("*LIVE*")
    result = testdir.runpytest("--xkill")
    result.stdout.fnmatch_lines("*TERMINATED*")
