import py
import pytest

from xprocess import XProcess


def pytest_addoption(parser):
    group = parser.getgroup(
        "xprocess", "managing external processes across test-runs [xprocess]"
    )
    group.addoption("--xkill", action="store_true", help="kill all external processes")
    group.addoption(
        "--xshow", action="store_true", help="show status of external process"
    )


def getrootdir(config):
    return config.cache.makedir(".xprocess")


def pytest_cmdline_main(config):
    xkill = config.option.xkill
    xshow = config.option.xshow
    if xkill or xshow:
        config._do_configure()
        tw = py.io.TerminalWriter()
        rootdir = getrootdir(config)
        xprocess = XProcess(config, rootdir)
    if xkill:
        return xprocess._xkill(tw)
    if xshow:
        return xprocess._xshow(tw)


@pytest.fixture(scope="session")
def xprocess(request):
    """Return session-scoped XProcess helper to manage long-running
    processes required for testing.
    """
    rootdir = getrootdir(request.config)
    return XProcess(request.config, rootdir)


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    logfiles = getattr(item.config, "_extlogfiles", None)
    report = yield
    if logfiles is None:
        return
    for name in sorted(logfiles):
        content = logfiles[name].read()
        if content:
            longrepr = getattr(report, "longrepr", None)
            if hasattr(longrepr, "addsection"):  # pragma: no cover
                longrepr.addsection("%s log" % name, content)


def pytest_unconfigure(config):
    """Reading processes exit status is a requirement of subprocess module,
    so each process instance should be properly waited upon. All file handles
    should also be closed by the end of the test run. This is done in order to
    avoid ResourceWarnings."""
    running_procs = getattr(config, "_running_procs", None)
    if running_procs:
        for p in running_procs:
            p.wait(config._proc_wait_timeout)
    file_handles = getattr(config, "_file_handles", None)
    if file_handles:
        for f in file_handles:
            f.close()
