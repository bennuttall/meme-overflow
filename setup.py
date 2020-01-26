"Setup script for the memeoverflow package"

import os
import sys
import io
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

if not sys.version_info >= (3, 6):
    raise RuntimeError('This application requires Python 3.6 or later')


def main():
    "Executes setup when this script is the top-level"
    import memeoverflow as app

    with io.open(os.path.join(HERE, 'description.rst'), 'r') as description:
        setup(
            name=app.__project__,
            version=app.__version__,
            author=app.__author__,
            author_email=app.__author_email__,
            url=app.__url__,
            platforms=app.__platforms__,
            requires=app.__requires__,
            python_requires=app.__python_requires__,
            keywords=app.__keywords__,
            classifiers=app.__classifiers__,
            install_requires=app.__requires__,
            description=app.__doc__,
            long_description=description.read(),
            packages=find_packages(),
        )


if __name__ == '__main__':
    main()
