import psutil
import pytest
from conftest import Test


class TestProcessTermination(Test):
    """test termination of process and children"""

    @pytest.mark.parametrize(
        "port,proc_name", [(6777, "s1"), (6778, "s2"), (6779, "s3"), (6780, "s4")]
    )
    def test_clean_shutdown(self, port, proc_name):
        self.start_server("started", proc_name, port)
        proc_info = self.get_info(proc_name)
        assert proc_info.isrunning()
        children = psutil.Process(proc_info.pid).children()
        assert len(children) >= 1
        self.terminate(proc_name)
        for child in children:
            assert not child.is_running()
