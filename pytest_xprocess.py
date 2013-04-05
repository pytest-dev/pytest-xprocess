
# content of conftest.py

import pytest
import subprocess
import textwrap
import py
import sys
import os

from pytest_cache import getrootdir

print_ = py.builtin.print_
std = py.std

def pytest_addoption(parser):
    group = parser.getgroup("xprocess",
        "managing external processes across test-runs [xprocess]")
    group.addoption('--xkill', action="store_true",
        help="kill all external processes")
    group.addoption('--xshow', action="store_true",
        help="show status of external process")

def pytest_cmdline_main(config):
    xkill = config.option.xkill
    xshow = config.option.xshow
    if xkill or xshow:
        config.pluginmanager.do_configure(config)
        tw = py.io.TerminalWriter()
        xprocess = XProcess(config)
        return do_killxshow(xprocess, tw, xkill)

def do_xkill(info, tw):
    if info.pid and info.isrunning():
        msg = "%r, pid %d" % (info.name, info.pid)
        if sys.platform == "win32":
            subprocess.check_call("taskkill /F /PID %s" % info.pid)
            tw.line("TERMINATED %s -- logfile %s" % (msg, info.logpath))
            #info.pidpath.dirpath().remove(ignore_error=True)
            return 0
        else:
            try:
                os.kill(info.pid, 9)
            except OSError:
                tw.line("FAILED killing %s" % msg, red=True)
                return 1
            else:
                tw.line("TERMINATED %s -- logfile %s" % (msg, info.logpath))
                info.pidpath.dirpath().remove(ignore_errors=True)
                return 0
    else:
        tw.line("no running %r process, pruning" % info.name, red=True)
        info.pidpath.dirpath().remove()
    return 1

def do_killxshow(xprocess, tw, xkill):
    ret = 0
    for p in xprocess.rootdir.listdir():
        info = xprocess.getinfo(p.basename)
        if xkill:
            ret = do_xkill(info, tw) or ret
        else:
            running = info.isrunning() and "LIVE" or "DEAD"
            tw.line("%s %s %s %s" %(info.pid, info.name, running,
                                        info.logpath,))
    return ret

class XProcessInfo:
    def __init__(self, path, name):
        self.name = name
        self.controldir = path.ensure(name, dir=1)
        self.logpath = self.controldir.join("xprocess.log")
        self.pidpath = self.controldir.join("xprocess.PID")
        if self.pidpath.check():
            self.pid = int(self.pidpath.read())
        else:
            self.pid = None

    def _isrunning_win32(self, pid):
        import ctypes, ctypes.wintypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        if handle == 0:
            return False
        exit_code = ctypes.wintypes.DWORD()
        is_running = (kernel32.GetExitCodeProcess(handle,
                        ctypes.byref(exit_code)) == 0)
        kernel32.CloseHandle(handle)
        return is_running or exit_code.value == 259

    def isrunning(self):
        if self.pid is not None:
            if sys.platform == "win32":
                return self._isrunning_win32(self.pid)
            try:
                os.kill(self.pid, 0)
                return True
            except OSError:
                pass
        return False


class XProcess:
    def __init__(self, config):
        self.config = config
        self.rootdir = getrootdir(self.config, ".xprocess")
        self.rootdir.ensure(dir=1)

    def getinfo(self, name):
        """ return Process Info for the given external process. """
        return XProcessInfo(self.rootdir, name)

    def ensure(self, name, preparefunc, restart=False):
        """ returns (PID, logfile) from a newly started or already
            running process.

        @param name: name of the external process, used for caching info
                     across test runs.

        @param preparefunc:
                called with a fresh empty CWD for the new process,
                must return (waitpattern, args) tuple where
                ``args`` are used to start the subprocess and ``waitpattern``
                must be found

        @param restart: force restarting the process if it is running.

        @return: (PID, logfile) logfile will be seeked to the end if the
                 server was running, otherwise seeked to the line after
                 where the waitpattern matched.
        """
        info = self.getinfo(name)
        if not restart and not info.isrunning():
            restart = True

        if restart:
            if info.pid is not None:
                try:
                    py.process.kill(info.pid)
                except OSError:
                    pass
                # wait?
            controldir = info.controldir
            controldir.remove()
            controldir.ensure(dir=1)
            wait, args = preparefunc(controldir)
            args = [str(x) for x in args]
            print ("%s$ %s" % (controldir, " ".join(args)))
            stdout = open(str(info.logpath), "w", 0)
            kwargs = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = 0x08
            else:
                kwargs["close_fds"] = True
            popen = subprocess.Popen(args, cwd=str(controldir),
                                     stdout=stdout, stderr=subprocess.STDOUT,
                                     **kwargs)
            pid = popen.pid
            info.pidpath.write(str(pid))
            stdout.close()
        f = info.logpath.open()
        if not restart:
            f.seek(0, 2)
        else:
            while 1:
                line = f.readline()
                if not line:
                    import time
                    time.sleep(0.1)
                if std.re.search(wait, line):
                   break

        logfiles = getattr(self.config, "_extlogfiles", {})
        logfiles[name] = f
        self.config._extlogfiles = logfiles
        return info.pid, f

@pytest.fixture(scope="session")
def xprocess(request):
    """ Return session-scoped XProcess helper to manage long-running
    processes required for testing.
    """
    return XProcess(request.config)

def pytest_runtest_makereport(__multicall__, item, call):
    logfiles = getattr(item.config, "_extlogfiles", None)
    if logfiles is None:
        return
    report = __multicall__.execute()
    for name in sorted(logfiles):
        content = logfiles[name].read()
        if content:
            longrepr = getattr(report, "longrepr", None)
            if hasattr(longrepr, "addsection"):
                longrepr.addsection("%s log" %name, content)
    return report

