# Reading processes exit status is a requirement of subprocess module,
# so each process instance should be properly waited upon. All file handles
# should also be closed by the end of the test run. This is done in order to
# avoid ResourceWarnings when env = {'shell': true'} in ProcessStarter"""


def test_hello(example):
    pass


def test_world(example):
    pass
