import sys

import psutil
import pytest
from conftest import Test


class TestProcessTermination(Test):
    """test termination of process and children"""

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")]
    )
    def test_clean_shutdown(self, port, proc_name):
        self.start_server("started", proc_name, port)
        proc_info = self.get_info(proc_name)
        assert proc_info.isrunning()
        children = psutil.Process(proc_info.pid).children(recursive=True)
        assert len(children) >= 1
        assert self.terminate(proc_name)
        for child in children:
            assert not child.is_running() or child.status() == psutil.STATUS_ZOMBIE

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")]
    )
    def test_terminate_no_pid(self, port, proc_name):
        self.start_server("started", proc_name, port)
        proc_info = self.get_info(proc_name)
        pid, proc_info.pid = proc_info.pid, None
        # call terminate through XProcessInfo instance
        # with pid=None to test edge case
        assert proc_info.terminate() == 0
        proc_info.pid = pid
        self.terminate(proc_name)

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")]
    )
    def test_terminate_only_parent(self, port, proc_name):
        self.start_server("started", proc_name, port)
        proc_info = self.get_info(proc_name)
        children = psutil.Process(proc_info.pid).children()
        assert len(children) >= 1
        assert self.terminate(proc_name, kill_proc_tree=False) == 1
        assert not proc_info.isrunning()
        for p in children:
            try:
                p.terminate()
            except Exception:
                pass

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="on windows SIGTERM is treated as an alias for kill()",
    )
    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")]
    )
    def test_sigkill_after_failed_sigterm(self, port, proc_name):
        # explicitly tell xprocess_starter fixture to make
        # server instance ignore SIGTERM
        self.start_server("started", proc_name, port, "--ignore-sigterm")
        pid = self.get_info(proc_name).pid
        # since terminate with sigterm will fail, set a lower
        # timeout before sending sigkill so tests won't take too long
        assert (
            self.terminate(proc_name, timeout=1) == 1
            or psutil.Process(pid).status() == psutil.STATUS_ZOMBIE
        )

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3")]
    )
    def test_return_value_on_failure(self, port, proc_name):
        self.start_server("started", proc_name, port)
        assert self.terminate(proc_name, timeout=-1) == -1
        try:
            # make sure hanging processes are not left behind
            psutil.Process(self.get_info(proc_name).pid).terminate()
        except psutil.NoSuchProcess:
            pass
