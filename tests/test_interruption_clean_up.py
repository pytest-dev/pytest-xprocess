from pathlib import Path


def test_processes_start(testdir):
    server_path = Path(__file__).parent.joinpath("server.py").absolute()
    testdir.makepyfile(
        """
        import sys
        import socket
        from xprocess import ProcessStarter

        def test_servers_start(request, xprocess):
            port = 6777
            server_path = %r

            class Starter(ProcessStarter):
                pattern = "started"
                args = [sys.executable, server_path, port]

            xprocess.ensure("server01", Starter)

            raise KeyboardInterrupt
        """
        % str(server_path)
    )
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines("*KeyboardInterrupt*")
    result = testdir.runpytest("--xshow")
    result.stdout.no_fnmatch_line("*LIVE*")
