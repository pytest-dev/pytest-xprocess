import itertools
import os
import signal
import sys
import traceback
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from time import sleep

import psutil
from py import std


class XProcessInfo:
    """Holds information of an active process instance represented by
    a XProcess Object and offers recursive termination functionality of
    said process tree."""

    def __init__(self, path, name):
        self.name = name
        self.controldir = path.ensure(name, dir=1)
        self.logpath = self.controldir.join("xprocess.log")
        self.pidpath = self.controldir.join("xprocess.PID")
        self.pid = int(self.pidpath.read()) if self.pidpath.check() else None

    def terminate(self, *, kill_proc_tree=True, timeout=20):
        """Recursively terminates process tree.

        This is the default behavior unless explicitly disabled by setting
        kill_proc_tree keyword-only parameter to false when calling
        ``XProcessInfo.terminate``.

        :param kill_proc_tree: Enable/disable recursive process tree
                               termination. Defaults to True.
        :param timeout: Maximum time in seconds to wait on process termination.
                        When timeout is reached after sending SIGTERM, this
                        method will attempt to SIGKILL the process and
                        return ``-1`` in case the operation times out again.
        return codes:
            0   no work to do
            1   terminated
            -1  failed to terminate"""
        if not self.pid:
            return 0
        try:
            parent = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return 0
        try:
            kill_list = [parent]
            if kill_proc_tree:
                kill_list += parent.children(recursive=True)
            for p in kill_list:
                p.send_signal(signal.SIGTERM)
            _, alive = psutil.wait_procs(kill_list, timeout=timeout)
            for p in alive:
                p.send_signal(signal.SIGKILL)
            _, alive = psutil.wait_procs(kill_list, timeout=timeout)
            if alive:  # pragma: no cover
                return -1
        except (psutil.Error, ValueError):
            return -1
        return 1

    def isrunning(self, ignore_zombies=True):
        """Returns whether the process is running or not.

        @param ignore_zombies: Treat zombie processes as terminated. Sometimes a
                               process that terminates itself during test execution
                               will become a zombie process during pytest's lifetime.

        @return: ``True`` if the process is running, ``False`` if it is not."""
        if self.pid is None:
            return False
        try:
            proc = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return False
        return proc.is_running() and (
            not ignore_zombies or proc.status() != psutil.STATUS_ZOMBIE
        )


class XProcess:
    """Main xprocess class. Represents a running process instance for which
    a set of actions is offered, such as process startup, command line actions
    and information fetching."""

    def __init__(self, config, rootdir, log=None, proc_wait_timeout=60):
        self.rootdir = rootdir

        self.config = config
        self.proc_wait_timeout = proc_wait_timeout

        self.file_handles = []
        self.running_procs = []

        class Log:
            def debug(self, msg, *args):
                if args:
                    print(msg % args)
                else:
                    print(msg)

        self.log = log or Log()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

    def getinfo(self, name):
        """Return Process Info for the given external process."""
        return XProcessInfo(self.rootdir, name)

    def ensure(self, name, preparefunc, restart=False):
        """Returns (PID, logfile) from a newly started or already
            running process.

        @param name: name of the external process, used for caching info
                     across test runs.

        @param preparefunc:
                A subclass of ProcessStarter.

        @param restart: force restarting the process if it is running.

        @return: (PID, logfile) logfile will be seeked to the end if the
                 server was running, otherwise seeked to the line after
                 where the waitpattern matched."""
        from subprocess import Popen, STDOUT

        info = self.getinfo(name)
        if not restart and not info.isrunning():
            restart = True

        if restart:
            if info.pid is not None:
                info.terminate()
            controldir = info.controldir.ensure(dir=1)
            starter = preparefunc(controldir, self)
            args = [str(x) for x in starter.args]
            self.log.debug("%s$ %s", controldir, " ".join(args))
            stdout = open(str(info.logpath), "wb", 0)
            kwargs = {"env": starter.env}
            if sys.platform == "win32":  # pragma: no cover
                kwargs["startupinfo"] = sinfo = std.subprocess.STARTUPINFO()
                sinfo.dwFlags |= std.subprocess.STARTF_USESHOWWINDOW
                sinfo.wShowWindow |= std.subprocess.SW_HIDE
            else:
                kwargs["close_fds"] = True
                kwargs["preexec_fn"] = os.setpgrp  # no CONTROL-C
            self.running_procs.append(
                Popen(args, cwd=str(controldir), stdout=stdout, stderr=STDOUT, **kwargs)
            )
            info.pid = pid = self.running_procs[-1].pid
            info.pidpath.write(str(pid))
            self.log.debug("process %r started pid=%s", name, pid)
            stdout.close()
        self.file_handles.append(info.logpath.open())
        if not restart:
            self.file_handles[-1].seek(0, 2)
        else:
            if not starter.wait(self.file_handles[-1]):
                raise RuntimeError(
                    "Could not start process {}, the specified "
                    "log pattern was not found within {} lines.".format(
                        name, starter.max_read_lines
                    )
                )
            self.log.debug("%s process startup detected", name)
        pytest_extlogfiles = self.config.__dict__.setdefault("_extlogfiles", {})
        pytest_extlogfiles[name] = self.file_handles[-1]
        self.getinfo(name)
        return info.pid, info.logpath

    def _infos(self):
        return (self.getinfo(p.basename) for p in self.rootdir.listdir())

    def _xkill(self, tw):
        ret = 0
        for info in self._infos():
            termret = info.terminate()
            ret = ret or (termret == 1)
            status = {
                1: "TERMINATED",
                -1: "FAILED TO TERMINATE",
                0: "NO PROCESS FOUND",
            }[termret]
            tmpl = "{info.pid} {info.name} {status}"
            tw.line(tmpl.format(**locals()))
        return ret

    def _xshow(self, tw):
        for info in self._infos():
            running = "LIVE" if info.isrunning() else "DEAD"
            tmpl = "{info.pid} {info.name} {running} {info.logpath}"
            tw.line(tmpl.format(**locals()))
        return 0


class ProcessStarter(ABC):
    """Describes the characteristics of a process to start and, waiting
    for a process to achieve a started state.

    @cvar env: The environment in which to invoke the process.

    @cvar timeout: The maximum time ProcessStarter.wait will hang waiting for a new
             line when trying to match pattern before raising TimeoutError.

    @cvar max_read_lines: The maximum amount of lines of the log that will be read
                    before presuming the attached process dead."""

    env = None
    timeout = 120
    max_read_lines = 50

    def __init__(self, control_dir, process):
        self.control_dir = control_dir
        self.process = process

    @property
    @abstractmethod
    def args(self):
        "The args to start the process."

    @property
    @abstractmethod
    def pattern(self):
        "The pattern to match when the process has started."

    def startup_check(self):
        """Used to assert process responsiveness after pattern match"""
        return True

    def wait_callback(self):
        """Assert that process is ready to answer queries using provided
        callback funtion. Will raise TimeoutError if self.callback does not
        return True before self.timeout seconds"""
        while True:
            sleep(0.1)
            if self.startup_check():
                return True
            if datetime.now() > self._max_time:
                raise TimeoutError(
                    "The provided startup callback could not assert process\
                    responsiveness within the specified time interval of {} \
                    seconds".format(
                        self.timeout
                    )
                )

    def wait(self, log_file):
        """Wait until the pattern is mached and callback returns successful."""
        self._max_time = datetime.now() + timedelta(seconds=self.timeout)
        lines = map(self.log_line, self.filter_lines(self.get_lines(log_file)))
        has_match = any(std.re.search(self.pattern, line) for line in lines)
        process_ready = self.wait_callback()
        return has_match and process_ready

    def filter_lines(self, lines):
        """fetch first <max_read_lines>, ignoring blank lines."""
        non_empty_lines = (x for x in lines if x.strip())
        return itertools.islice(non_empty_lines, self.max_read_lines)

    def log_line(self, line):
        """Write line to process log file."""
        self.process.log.debug(line)
        return line

    def get_lines(self, log_file):
        """Read and yield one line at a time from log_file. Will raise
        TimeoutError if pattern is not matched before self.timeout
        seconds."""
        while True:
            line = log_file.readline()
            if not line:
                std.time.sleep(0.1)
            if datetime.now() > self._max_time:
                raise TimeoutError(
                    "The provided start pattern {} could not be matched \
                    within the specified time interval of {} seconds".format(
                        self.pattern, self.timeout
                    )
                )
            yield line
