import importlib.util

import pytest_xprocess
from pytest_xprocess import getrootdir
from pytest_xprocess import ProcessStarter
from pytest_xprocess import XProcess
from pytest_xprocess import XProcessInfo
from pytest_xprocess import XProcessResources
from xprocess import ProcessStarter as InternalProcessStarter
from xprocess import XProcess as InternalXProcess
from xprocess import XProcessInfo as InternalXProcessInfo
from xprocess import XProcessResources as InternalXProcessResources
from xprocess.pytest_xprocess import getrootdir as internal_getrootdir


def test_top_level_pytest_xprocess_spec():
    spec = importlib.util.find_spec("pytest_xprocess")
    assert spec is not None
    assert spec.origin is not None


def test_top_level_pytest_xprocess_exports():
    assert getrootdir is internal_getrootdir
    assert ProcessStarter is InternalProcessStarter
    assert XProcess is InternalXProcess
    assert XProcessInfo is InternalXProcessInfo
    assert XProcessResources is InternalXProcessResources
    assert hasattr(pytest_xprocess, "xprocess")
