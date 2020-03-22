"Setup script for the memeoverflow package"

import os
import sys
import io
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

if not sys.version_info >= (3, 6):
    raise RuntimeError('This application requires Python 3.6 or later')

__project__ = 'memeoverflow'
__version__ = '0.7.1'
__author__ = 'Ben Nuttall'
__author_email__ = 'ben@bennuttall.com'
__url__ = 'https://github.com/bennuttall/meme-overflow'
__platforms__ = ['ALL']
__requires__ = [
    'requests',
    'twython',
    'logzero',
]
__extra_requires__ = {
    'test':  ['pytest', 'coverage', 'mock'],
}
__python_requires__ = '>=3.6'
__keywords__ = [
    'twitter',
    'stackoverflow',
    'stackexchange',
    'meme',
    'imgflip',
]
__classifiers__ = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Games/Entertainment",
]
__license__ = [
    c.rsplit('::', 1)[1].strip()
    for c in __classifiers__
    if c.startswith('License ::')
][0]

def main():
    "Executes setup when this script is the top-level"

    with io.open(os.path.join(HERE, 'description.rst'), 'r') as description:
        setup(
            name=__project__,
            version=__version__,
            author=__author__,
            author_email=__author_email__,
            url=__url__,
            platforms=__platforms__,
            requires=__requires__,
            python_requires=__python_requires__,
            keywords=__keywords__,
            classifiers=__classifiers__,
            install_requires=__requires__,
            extras_require=__extra_requires__,
            description=__doc__,
            long_description=description.read(),
            packages=find_packages(),
        )


if __name__ == '__main__':
    main()
