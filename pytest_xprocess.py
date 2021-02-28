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

    with XProcess(request.config, rootdir) as xproc:
        yield xproc

    """Reading processes exit status is a requirement of subprocess module,
    so each process instance should be properly waited upon."""
    for p in xproc.running_procs:
        p.wait(xproc.proc_wait_timeout)

    request.config._xprocess_file_handles += xproc.file_handles


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


def pytest_configure(config):
    config.__dict__.setdefault("_xprocess_file_handles", [])


def pytest_unconfigure(config):
    """All logfile handles should be closed by the end of the test run.
    This is done in order to avoid ResourceWarnings."""
    for f in config._xprocess_file_handles:
        f.close()
