=========================
Releasing pytest-xprocess
=========================

This document describes the steps to make a new ``pytest-xprocess`` release.

Version
-------

``master`` should always be green and a potential release candidate. ``pytest-xprocess`` follows
semantic versioning, so given that the current version is ``X.Y.Z``, to find the next version number
one needs to look at the ``changelog`` file for the latest section marked as ``Unreleased``:

Steps
-----

To publish a new release ``X.Y.Z``, the steps are as follows:

#. Create a new branch named ``release-X.Y.Z`` from the latest ``master``.

#. Install ``tox`` in a virtualenv::

    $ pip install tox

#. Update the necessary files with::

    $ tox -e release -- X.Y.Z

#. Commit and push the branch for review.

#. Once PR is **green** and **approved**, create and push a tag::

    $ export VERSION=X.Y.Z
    $ git tag v$VERSION release-$VERSION
    $ git push git@github.com:pytest-dev/pytest-xprocess.git v$VERSION

That will build the package and publish it on ``PyPI`` automatically.
