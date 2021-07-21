from pathlib import Path


def test_functional_work_flow(testdir, tcp_port):
    server_path = Path(__file__).parent.joinpath("server.py").absolute()
    testdir.makepyfile(
        """
        import sys
        import socket
        from xprocess import ProcessStarter

        def test_server(request, xprocess):
            port = %r
            data = "spam\\n"
            server_path = %r

            class Starter(ProcessStarter):
                pattern = "started"
                max_read_lines = 200
                args = [sys.executable, server_path, port]

            # required so test won't hang on pytest_unconfigure
            xprocess.proc_wait_timeout = 1

            xprocess.ensure("server_workflow_test", Starter)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("localhost", port))
                sock.sendall(bytes(data, "utf-8"))
                received = str(sock.recv(1024), "utf-8")
                assert received == data.upper()
    """
        % (tcp_port, str(server_path))
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines("*1 passed*")
    result = testdir.runpytest("--xshow")
    result.stdout.fnmatch_lines("*LIVE*")
    result = testdir.runpytest("--xkill")
    result.stdout.fnmatch_lines("*TERMINATED*")
