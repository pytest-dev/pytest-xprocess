0.17.0 (2020-11-26)
-------------------

- :class:`ProcessStarter` now has :meth:`startup_check`. This method can be optionaly overridden and will be called upon to check process responsiveness
  after :attr:`ProcessStarter.pattern` is matched. By default, :meth:`XProcess.ensure` will only attempt to match :attr:`ProcessStarter.pattern` when starting a process, if matched, xprocess
  will consider the process as ready to answer queries. If :meth:`startup_check` is provided though, its return value will also be considered to determine if the process has been
  successfully started. If :meth:`startup_check` returns `True` after :attr:`ProcessStarter.pattern` has been matched, :meth:`XProcess.ensure` will return sucessfully. In contrast, if
  :meth:`startup_check` does not return `True` before timing out, :meth:`XProcess.ensure` will raise a `TimeoutError` exception.
- Remove deprecated :meth:`xprocess.CompatStarter`

0.16.0 (2020-10-29)
-------------------

- :class:`ProcessStarter` now has a new `timeout` class variable optionaly overridden to define the maximum time :meth:`xprocess.ensure` should wait for process output when trying to match :attr:`ProcessStarter.pattern`. Defaults to 120 seconds.
- The number of lines in the process logfile watched for :attr:`ProcessStarter.pattern` is now configurable and can be changed by setting :attr:`ProcessStarter.max_read_lines` to the desired value. Defaults to 50 lines.
- Make :meth:`XProcessInfo.isrunning` ignore zombie processes by default. Pass ``ignore_zombies=False`` to get the previous behavior, which was to consider zombie processes as running.

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
------------------

- Initial release
