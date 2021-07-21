from pathlib import Path


def test_interruption_cleanup(testdir, tcp_port):
    server_path = Path(__file__).parent.joinpath("server.py").absolute()
    testdir.makepyfile(
        """
        import sys
        import socket
        from xprocess import ProcessStarter

        def test_servers_start(request, xprocess):
            port = %r
            server_path = %r

            class Starter(ProcessStarter):
                terminate_on_interrupt = True
                pattern = "started"
                args = [sys.executable, server_path, port]

            xprocess.ensure("server_test_interrupt", Starter)

            raise KeyboardInterrupt
        """
        % (tcp_port, str(server_path))
    )
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines("*KeyboardInterrupt*")
    result = testdir.runpytest("--xshow")
    result.stdout.no_fnmatch_line("*LIVE*")


def test_interruption_does_not_cleanup(testdir, tcp_port):
    server_path = Path(__file__).parent.joinpath("server.py").absolute()
    testdir.makepyfile(
        """
        import sys
        import socket
        from xprocess import ProcessStarter

        def test_servers_start(request, xprocess):
            port = %r
            server_path = %r

            class Starter(ProcessStarter):
                pattern = "started"
                args = [sys.executable, server_path, port]

            xprocess.ensure("server_test_interrupt_no_terminate", Starter)

            raise KeyboardInterrupt
        """
        % (tcp_port, str(server_path))
    )
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines("*KeyboardInterrupt*")
    result = testdir.runpytest("--xshow")
    result.stdout.fnmatch_lines("*LIVE*")
    result = testdir.runpytest("--xkill")
    result.stdout.fnmatch_lines("*TERMINATED*")
