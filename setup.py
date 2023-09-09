from setuptools import setup

if __name__ == "__main__":
    setup(
        name="pytest-xprocess",
        # this is for GitHub's dependency graph
        install_requires=["pytest>=2.8", "psutil"],
    )
