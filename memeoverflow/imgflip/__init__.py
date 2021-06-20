from time import sleep
from json import JSONDecodeError

import requests
from requests.exceptions import RequestException

from .memes import MEMES
from ..exc import ImgFlipError


API_URL = 'https://api.imgflip.com/caption_image'


class ImgFlip:
    """
    Wrapper class for imgflip API interaction

    :type username: str
    :param username: imgflip account username
    
    :type password: str
    :param password: imgflip account password
    """
    def __init__(self, *, username, password):
        self._username = username
        self._password = password

    def __repr__(self):
        return f"<ImgFlip username='{self.username}'>"

    @property
    def username(self):
        return self._username

    def make_meme(self, *, meme, text_parts):
        "Generate a meme with the supplied text, and return its URL"
        data = {
            'username': self._username,
            'password': self._password,
            'template_id': MEMES[meme]['id'],
            'text0': text_parts[0],
            'text1': text_parts[1],
        }
        r = requests.post(API_URL, data=data)
        try:
            r.raise_for_status()
            img_url = r.json()['data']['url']
            return img_url
        except (RequestException, JSONDecodeError, KeyError) as e:
            raise ImgFlipError("Failed to make meme") from e
