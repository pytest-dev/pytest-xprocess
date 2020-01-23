from setuptools import setup

if __name__ == "__main__":
    setup(
        name='pytest-xprocess',
        description='pytest plugin to manage external processes across test runs',
        long_description=open("README.rst").read(),
        use_scm_version=True,
        license="MIT",
        author='Holger Krekel',
        author_email='holger@merlinux.eu',
        url='https://github.com/pytest-dev/pytest-xprocess/',
        py_modules=['pytest_xprocess', 'xprocess'],
        entry_points={'pytest11': ['xprocess = pytest_xprocess']},
        install_requires=['pytest>=2.8', 'psutil'],
        setup_requires=["setuptools_scm"],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Operating System :: Microsoft :: Windows',
            'Topic :: Software Development :: Testing',
            'Topic :: Software Development :: Libraries',
            'Topic :: Utilities',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
    )
