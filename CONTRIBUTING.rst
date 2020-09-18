How to contribute
=================

All contributions are greatly appreciated!


Setting up your development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   Fork pytest-xprocess to your GitHub account by clicking the `Fork`_ button.
-   `Clone`_ the main repository (not your fork) to your local machine.

    .. code-block:: text

        $ git clone https://github.com/pytest-dev/pytest-xprocess
        $ cd pytest-xprocess

-   Add your fork as a remote to push your contributions.Replace
    ``{username}`` with your username.

    .. code-block:: text

        git remote add fork https://github.com/{username}/pytest-xprocess

-   Using `Tox`_, create a virtual environment and install xprocess in editable mode with development dependencies.

    .. code-block:: text

        $ tox -e dev
        $ source venv/bin/activate

.. _Fork: https://github.com/pallets/cachelib/fork
.. _Clone: https://help.github.com/en/articles/fork-a-repo#step-2-create-a-local-clone-of-your-fork
.. _Tox: https://tox.readthedocs.io/en/latest/

Start Coding
~~~~~~~~~~~~

-   Create a new branch to identify what feature you are working on.

    .. code-block:: text

        $ git fetch origin
        $ git checkout -b your-branch-name origin/master

-   Make your changes
-   Include tests that cover any code changes you make and run them
    as described below.
-   Push your changes to your fork.
    `create a pull request`_ describing your changes.

    .. code-block:: text

        $ git push --set-upstream fork your-branch-name

.. _create a pull request: https://help.github.com/en/articles/creating-a-pull-request

How to run tests
~~~~~~~~~~~~~~~~

You can run the test suite for the current environment with

    .. code-block:: text

        $ pytest

To run the full test suite for all supported python versions

    .. code-block:: text

        $ tox

Obs. CI will run tox when you submit your pull request, so this is optional.
