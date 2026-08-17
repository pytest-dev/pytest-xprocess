from xprocess.pytest_xprocess import get_log_files


def test_get_log_files_excludes_directories(tmp_path):
    """Regression test for #135.

    get_log_files() should only return actual log files, not
    subdirectories whose name happens to end in 'log'.
    """
    proc_dir = tmp_path / "proc1"
    proc_dir.mkdir()

    # A subdirectory literally named "log" should NOT be returned.
    (proc_dir / "log").mkdir()

    # A real log file should be returned.
    real_log = proc_dir / "real.log"
    real_log.write_text("some log output")

    log_files = get_log_files(str(tmp_path))

    assert str(real_log) in log_files
    assert str(proc_dir / "log") not in log_files
    assert len(log_files) == 1
