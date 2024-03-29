=========================
Releasing pytest-xprocess
=========================

This document describes the steps to make a new ``pytest-xprocess`` release.

Version
-------

``master`` should always be green and a potential release candidate. ``pytest-xprocess`` follows
semantic versioning, so given that the current version is ``X.Y.Z``, to find the next version number
one needs to look at the ``changelog`` file for the latest section marked as ``Unreleased``

Steps
-----

#. Create a new branch named ``release-X.Y.Z`` from the latest ``master``.

#. Create and activate a virtualenv::

    $ python -m venv venv && source venv/bin/activate

#. Install ``tox``::

    $ pip install tox

#. Run the test suite and ensure everything passes::

    $ tox

#. Commit and push the branch for review.

#. Once PR is **green** and **approved**, create and push a tag::

    $ export VERSION=X.Y.Z
    $ git tag $VERSION release-$VERSION
    $ git push git@github.com:pytest-dev/pytest-xprocess.git $VERSION

#. Merge ``release-X.Y.Z`` branch into master.
