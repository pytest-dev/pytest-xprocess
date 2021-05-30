import py
import pytest

from _internal import getrootdir
from xprocess import XProcess


def pytest_addoption(parser):
    group = parser.getgroup(
        "xprocess", "managing external processes across test-runs [xprocess]"
    )
    group.addoption("--xkill", action="store_true", help="kill all external processes")
    group.addoption(
        "--xshow", action="store_true", help="show status of external process"
    )


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
    """yield session-scoped XProcess helper to manage long-running
    processes required for testing."""
    rootdir = getrootdir(request.config)
    with XProcess(request.config, rootdir) as xproc:
        # pass in xprocess object into pytest_unconfigure
        # through config for proper cleanup during teardown
        request.config._xprocess = xproc
        yield xproc


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
    try:
        xprocess = config._xprocess
    except AttributeError:
        # xprocess fixture was not used
        pass
    else:
        xprocess._clean_up_resources()


def pytest_configure(config):
    config.pluginmanager.register(InterruptionHandler())


class InterruptionHandler:
    """The purpose of this class is exposing the
    config object containing references necessary
    to properly clean-up in the event of an exception
    during test runs"""

    def pytest_configure(self, config):
        self.config = config

    def info_objects(self):
        return self.config._xprocess._info_objects

    def interruption_clean_up(self):
        try:
            xprocess = self.config._xprocess
        except AttributeError:
            pass
        else:
            for info, terminate_on_interrupt in self.info_objects():
                if terminate_on_interrupt:
                    info.terminate()
            xprocess._clean_up_resources()

    def pytest_keyboard_interrupt(self, excinfo):
        self.interruption_clean_up()

    def pytest_internalerror(self, excrepr, excinfo):
        self.interruption_clean_up()
