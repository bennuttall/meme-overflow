import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="memeoverflow",
    version="0.1.0",
    author="Ben Nuttall",
    description="Take questions posted on a particular Stack Exchange site, generate a meme out of it and tweet it",
    license="BSD",
    keywords=[],
    url="",
    packages=find_packages(),
    requires=[
        'requests',
        'twython',
    ],
    long_description=read('README.md'),
)
