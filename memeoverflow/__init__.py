"Simple framework for Twitter bots creating memes from Stack Exchange questions"

from .memeoverflow import MemeOverflow, MemeDatabase


__project__ = 'memeoverflow'
__version__ = '0.4.0'
__author__ = 'Ben Nuttall'
__author_email__ = 'ben@bennuttall.com'
__url__ = 'https://github.com/bennuttall/meme-overflow'
__platforms__ = ['ALL']
__requires__ = [
    'requests',
    'twython',
    'logzero',
]
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
