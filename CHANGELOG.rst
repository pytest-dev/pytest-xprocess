0.23.0 (2023-09-23)
-------------------

- Drop support for Python 3.7
- Add support for Python 3.11
- Remove dependency on `py`

0.22.2 (2023-01-05)
-------------------

- Python 3.10 is now officially supported
- `surrogateescape` will now be used as error handling strategy for encode/decode operations. (`#127 <https://github.com/pytest-dev/pytest-xprocess/pull/127>`)
- Make log files persistency, added in `0.21.0`, optional, defaulting to True. The previous logging behavior (prior to `0.21.0`) can be enabled by setting `persist_logs` flag to `False` when calling `XProcess.ensure`. (`#122 <https://github.com/pytest-dev/pytest-xprocess/pull/122>`_)
- Fix resource warnings due to leaked internal file handles (`#121 <https://github.com/pytest-dev/pytest-xprocess/pull/121>`_)
- Ignore zombie processes which are erroneously considered alive with python 3.11
  (`#117 <https://github.com/pytest-dev/pytest-xprocess/pull/118>`_)

0.21.0 (2022-11-27)
-------------------

- Explicitly add `py` package as a dependency, fixing issue with `pytest` >= 7.2.0
- Process log files will not be overwritten for each new process anymore, making it
  easier to debug issues that occurred in the middle of failed test runs

0.20.0 (2022-08-29)
-------------------

- Cleanup reminders will now only be printed for verbosity
  levels equal or greater than 1

0.19.0 (2022-05-23)
-------------------

- drop support for python 3.5 and 3.6
- reorganize internals. ``pytest-xprocess`` is now a package and all resources
  used by running processes are kept as instances of :class:``XProcessResources``.

0.18.1 (2021-07-27)
-------------------

- Fix bug with previous release where internal module was missing

0.18.0 (2021-07-21)
-------------------

- :method:`ProcessInfo.terminate` will now terminate outer leaves in process
  tree first and work its way towards root process. For example, if a process
  has child and grandchild, xprocess will terminate first child and grandchild
  and only then will the root process receive a termination signal.

- :class:`ProcessStarter` now has attr:`terminate_on_interrupt`. This flag will
  make xprocess attempt to terminate and clean up all started process resources
  upon interruptions during pytest runs (`CTRL+C`, `SIGINT` and internal errors)
  when set to `True`. It will default to `False`, so if the described behaviour
  is desired the flag must be explicitly set `True`.

- Add a new `popen_kwargs` variable to `ProcessStarter`, this variable can
  be used for passing keyword values to the `subprocess.Popen` constructor,
  giving the user more control over how the process is initialized.

0.17.1 (2021-02-28)
-------------------

- Fix `ResourceWarning` in :meth:`XProcess.ensure` caused by not properly
  waiting on process exit and leaked File handles

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
