0.14.0
------
Unreleased

- Now ``XProcessInfo.terminate`` will by default also terminate the entire
  process tree. This is safer as there's no risk of leaving lingering processes
  behind. If for some reason you need the previous behavior of only terminating
  the root process, pass ```kill_proc_tree=False`` to ``XProcessInfo.terminate``.

0.13.1
------
released Jan 29

- Drop support for Python 2.6 and 3.4.

- Ignore empty lines in log files when looking for the pattern that indicates
  a process has started.

0.13.0
------
Unreleased

- Never released due to deploy issues.

0.12.1
------
Released Jun 7, 2017

- Fixed example in README.md

0.12
----
Relased Jun 6, 2017

- #3: :meth:`XProcess.ensure` now accepts preferably a ProcessStarter
  subclass to define and customize the process startup behavior. Passing a
  simple function is deprecated and will be removed in a future release.

0.11.1
------
Released May 31, 2017

- Restored :meth:`XProcessInfo.kill()` as alias for
  :meth:`XProcessInfo.terminate()` for API compatibility.

0.11
----
Released May 18, 2017

- When tearing down processes (through ``--xkill``), the
  more polite SIGTERM is used before invoking SIGKILL,
  allowing the process to cleanly shutdown. See
  https://github.com/pytest-dev/pytest-xprocess/issues/1
  for more details.

- :meth:`XProcessInfo.kill()` is deprecated.

0.10
----
Released May 15, 2017

- Project `now hosted on Github
  <https://github.com/pytest-dev/pytest-xprocess/>`_.

0.9.1
-----
Released Jul 15, 2015

- Don't use `__multicall__` in pytest hook

0.9
---
Released Jul 15, 2015

- Fix issue Log calls without parameters now print the correct message
  instead of an empty tuple. See
  https://bitbucket.org/pytest-dev/pytest-xprocess/pull-request/3 for more
  info.

- Use 3rd party `psutil` library for process handling

0.8
---
Released Oct 4, 2013

- Support python3 (tested on linux/win32)

- Split out pytest independent process support into `xprocess.py`

- Add method:`xProcessInfo.kill` and some smaller refactoring

- Fix various windows related Popen / killing details

- Add tests

0.7
---

- Initial release
