from setuptools import setup

if __name__ == "__main__":
    setup(
        name='pytest-xprocess',
        description='pytest plugin to manage external processes across test runs',
        long_description=open("README.rst").read(),
        version='0.12',
        license="MIT",
        author='Holger Krekel',
        author_email='holger@merlinux.eu',
        url='https://github.com/pytest-dev/pytest-xprocess/',
        py_modules=['pytest_xprocess', 'xprocess'],
        entry_points={'pytest11': ['xprocess = pytest_xprocess']},
        install_requires=['pytest-cache', 'pytest>=2.3.5', 'psutil'],
    )
