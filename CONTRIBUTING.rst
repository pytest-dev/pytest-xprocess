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

-   Create a new virtualenv.

    .. code-block:: text

        $ python3 -m venv env
        $ . env/bin/activate

-   Install pytest-xprocess in editable mode with development dependencies.

    .. code-block:: text

        $ pip install -e . -r requirements/dev.txt

-   Finally, install the pre-commit hooks and you are
    are all set to start coding.

    .. code-block:: text

        $ pre-commit install

.. _Fork: https://github.com/pallets/cachelib/fork
.. _Clone: https://help.github.com/en/articles/fork-a-repo#step-2-create-a-local-clone-of-your-fork


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

.. _committing as you go: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _create a pull request: https://help.github.com/en/articles/creating-a-pull-request


How to run tests
~~~~~~~~~~~~~~~~

To run the tests in the current environment, just use pytest.

.. code-block:: text

    $ pytest

Optionally, you can run the test suite with tox in multiple environments

.. code-block:: text

    $ tox
