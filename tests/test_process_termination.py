import sys
from pathlib import Path

import psutil
import pytest

from xprocess import ProcessStarter

server_path = Path(__file__).parent.joinpath("server.py").absolute()


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_clean_shutdown(port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.isrunning()
    children = psutil.Process(info.pid).children()
    assert info.terminate()
    for child in children:
        assert not child.is_running() or child.status() == psutil.STATUS_ZOMBIE


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_terminate_no_pid(port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    pid, info.pid = info.pid, None
    # call terminate through XProcessInfo instance
    # with pid=None to test edge case
    assert info.terminate() == 0
    info.pid = pid
    info.terminate()


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_terminate_only_parent(port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, port]

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
@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_sigkill_after_failed_sigterm(port, proc_name, xprocess):
    # explicitly tell xprocess_starter fixture to make
    # server instance ignore SIGTERM
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, port, "--ignore-sigterm"]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    # since terminate with sigterm will fail, set a lower
    # timeout before sending sigkill so tests won't take too long
    assert (
        info.terminate(timeout=2) == 1
        or psutil.Process(info.pid).status() == psutil.STATUS_ZOMBIE
    )


@pytest.mark.parametrize("port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")])
def test_return_value_on_failure(port, proc_name, xprocess):
    class Starter(ProcessStarter):
        pattern = "started"
        args = [sys.executable, server_path, port]

    xprocess.ensure(proc_name, Starter)
    info = xprocess.getinfo(proc_name)
    assert info.terminate(timeout=-1) == -1
    try:
        # make sure hanging processes are not left behind
        psutil.Process(info.pid).terminate()
    except psutil.NoSuchProcess:
        pass
