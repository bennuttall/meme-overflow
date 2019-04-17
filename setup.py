import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="memeoverflow",
    version="0.3.2",
    author="Ben Nuttall",
    description="Take questions posted on a particular Stack Exchange site, generate a meme out of it and tweet it",
    license="OSI Approved :: BSD License",
    keywords=[
        'stackexchange',
        'stackoverflow',
        'meme',
        'twitter',
    ],
    url="https://github.com/bennuttall/meme-overflow",
    packages=find_packages(),
    requires=[
        'requests',
        'twython',
        'logzero',
    ],
    long_description=read('description.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Games/Entertainment",
    ]
)
