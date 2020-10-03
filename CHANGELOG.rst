0.15.0 (2020-10-03)
-------------------

- pytest-xprocess now uses a sub-directory of `.pytest_cache` to store process related files.
- Drop support for Python 2.7
- Fixed bug when non-ascii characters were written to stdout by external
  process
- Removed deprecated :meth:`XProcessInfo.kill`

0.14.0 (2020-09-24)
-------------------

- Now ``XProcessInfo.terminate`` will by default also terminate the entire
  process tree. This is safer as there's no risk of leaving lingering processes
  behind. If for some reason you need the previous behavior of only terminating
  the root process, pass ```kill_proc_tree=False`` to ``XProcessInfo.terminate``.

0.13.1 (2020-01-29)
-------------------

- Drop support for Python 2.6 and 3.4.

- Ignore empty lines in log files when looking for the pattern that indicates
  a process has started.

0.13.0 (UNRELEASED)
-------------------

- Never released due to deploy issues.

0.12.1 (2017-06-07)
-------------------

- Fixed example in README.md

0.12.0 (2017-06-06)
-------------------

- #3: :meth:`XProcess.ensure` now accepts preferably a ProcessStarter
  subclass to define and customize the process startup behavior. Passing a
  simple function is deprecated and will be removed in a future release.

0.11.1 (2017-05-31)
-------------------

- Restored :meth:`XProcessInfo.kill()` as alias for
  :meth:`XProcessInfo.terminate()` for API compatibility.

0.11 (2017-05-18)
-----------------

- When tearing down processes (through ``--xkill``), the
  more polite SIGTERM is used before invoking SIGKILL,
  allowing the process to cleanly shutdown. See
  https://github.com/pytest-dev/pytest-xprocess/issues/1
  for more details.

- :meth:`XProcessInfo.kill()` is deprecated.

0.10 (2017-05-15)
-----------------

- Project `now hosted on Github
  <https://github.com/pytest-dev/pytest-xprocess/>`_.

0.9.1 (2015-07-15)
------------------

- Don't use `__multicall__` in pytest hook

0.9 (2015-07-15)
----------------

- Fix issue Log calls without parameters now print the correct message
  instead of an empty tuple. See
  https://bitbucket.org/pytest-dev/pytest-xprocess/pull-request/3 for more
  info.

- Use 3rd party `psutil` library for process handling

0.8.0 (2013-10-04)
------------------

- Support python3 (tested on linux/win32)

- Split out pytest independent process support into `xprocess.py`

- Add method:`xProcessInfo.kill` and some smaller refactoring

- Fix various windows related Popen / killing details

- Add tests

0.7.0 (2013-04-05)
---

- Initial release
