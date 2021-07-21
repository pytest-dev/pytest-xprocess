import sys
from pathlib import Path

import psutil
import pytest

from xprocess import ProcessStarter

server_path = Path(__file__).parent.joinpath("server.py").absolute()


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_clean_shutdown(tcp_port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.isrunning()
    children = psutil.Process(info.pid).children()
    assert info.terminate() == 1
    for child in children:
        assert not child.is_running() or child.status() == psutil.STATUS_ZOMBIE


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_terminate_no_pid(tcp_port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    pid, info.pid = info.pid, None
    # call terminate through XProcessInfo instance
    # with pid=None to test edge case
    assert info.terminate() == 0
    info.pid = pid
    info.terminate()


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_terminate_only_parent(tcp_port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    children = psutil.Process(info.pid).children()
    assert info.terminate(kill_proc_tree=False) == 1
    assert not info.isrunning()
    for p in children:
        try:
            p.terminate()
        except Exception:
            pass


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="on windows SIGTERM is treated as an alias for kill()",
)
@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_sigkill_after_failed_sigterm(tcp_port, proc_name, xprocess):
    # explicitly tell xprocess_starter fixture to make
    # server instance ignore SIGTERM
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port, "--ignore-sigterm"]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    # since terminate with sigterm will fail, set a lower
    # timeout before sending sigkill so tests won't take too long
    assert (
        info.terminate(timeout=2) == 1
        or psutil.Process(info.pid).status() == psutil.STATUS_ZOMBIE
    )


@pytest.mark.parametrize("proc_name", ["s1", "s2", "s3"])
def test_return_value_on_failure(tcp_port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, tcp_port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.terminate(timeout=-1) == -1
    try:
        # make sure hanging processes are not left behind
        psutil.Process(info.pid).terminate()
    except psutil.NoSuchProcess:
        pass
