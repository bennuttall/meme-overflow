from .db import MemeDatabase
from .imgflip import MEMES
from .exc import StackExchangeNoKeyWarning

import random
from time import sleep
from io import BytesIO
import html
import warnings

import requests
from requests.exceptions import RequestException
from twython import Twython, TwythonError
from logzero import logger


imgflip_url = 'https://api.imgflip.com/caption_image'
stack_url = 'https://api.stackexchange.com/2.2/questions'


def _validate_keys(name, d, keys):
    """
    Assert that all keys exist in d, and that they are non-empty strings.
    If any invalid keys found, raise TypeError.
    """
    try:
        for key in keys:
            assert isinstance(d[key], str)
            assert len(d[key]) > 0
    except TypeError:
        raise TypeError(f'{name} is not a dict')
    except KeyError:
        raise TypeError(
            f"Missing dict keys for {name}. Expecting: {', '.join(keys)}"
        )
    except AssertionError:
        raise TypeError(f'Invalid key values for {name}. Keys must be non-empty strings.')
    return True

def _validate_api_keys(twitter, imgflip, stackexchange):
    "Check all API keys are in valid format, otherwise raise TypeError."
    twitter_keys = ('con_key', 'con_sec', 'acc_tok', 'acc_sec')
    _validate_keys('Twitter', twitter, twitter_keys)
    imgflip_keys = ('user', 'pass')
    _validate_keys('imgflip', imgflip, imgflip_keys)
    stackexchange_keys = ('site', )
    _validate_keys('Stack Exchange', stackexchange, stackexchange_keys)
    return True


class MemeOverflow:
    """
    Class for generating and tweeting memes of questions from a given
    StackExchange site

    :param dict twitter:
        Expected keys: con_key, con_sec, acc_tok, acc_sec (Twitter API keys)

    :param dict imgflip:
        Expected keys: user, pass (imgflip account)

    :param dict stackexchange:
        Expects key: site (Stack Exchange site name)
        Optional key: key (Stack Exchange API key)

    :param str db_path:
        Path to the sqlite database file
    """
    def __init__(self, twitter, imgflip, stackexchange, db_path):
        _validate_api_keys(twitter, imgflip, stackexchange)

        self.twitter = Twython(
            twitter['con_key'],
            twitter['con_sec'],
            twitter['acc_tok'],
            twitter['acc_sec']
        )
        self.imgflip = imgflip
        self.stackexchange = stackexchange
        self.db = MemeDatabase(site=stackexchange['site'], db_path=db_path)

        if 'key' not in self.stackexchange:
            warnings.warn(
                'No StackExchange API key provided, limited use may apply',
                StackExchangeNoKeyWarning,
            )

    def __repr__(self):
        return f"<MemeOverflow object for site {self.stackexchange['site']}>"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self):
        while True:
            questions = self.get_se_questions()
            for q in questions:
                tweeted = self.generate_meme_and_tweet(q)
                if tweeted:
                    sleep(60*5)
            sleep(60*5)

    def get_se_questions(self, n=100):
        "Retreive n questions from the StackExchange site and return as a list"
        params = {
            'pagesize': n,
            'site': self.stackexchange['site'],
            'key': self.stackexchange.get('key', None),
        }
        try:
            r = requests.get(stack_url, params)
            return r.json()['items']
        except (KeyError, RequestException) as e:
            logger.error(f'{e.__class__.__name__}: {e}')
            return []

    def choose_meme_template(self, text):
        """
        Choose a meme for the supplied text. If the text fits one of the
        templates well, it will use that one, otherwise it will be random. If
        text does not work with randomly chosen template, this method will be
        called again. Some templates move text to the second row or add their
        own second row of text to complete the meme.

        Return (meme_name, text0, text1)
        """
        text0 = text
        text1 = None

        if text.lower().startswith("is this "):
            meme = 'IS_THIS_A_PIGEON'
            text0 = "is this"
            text1 = text[8:]
        elif 'possible' in text.lower() and text.endswith('?'):
            meme = 'WELL_YES_BUT_ACTUALLY_NO'
        elif text.count('"') == 2:
            meme = 'DR_EVIL_LASER'
        elif text.lower().startswith('if') and text.endswith('?'):
            meme = 'PHILOSORAPTOR'
        else:
            meme = random.choice(list(MEMES.keys()))

            if meme in (
                'IS_THIS_A_PIGEON',
                'WELL_YES_BUT_ACTUALLY_NO',
                'DR_EVIL_LASER',
                'PHILOSORAPTOR',
            ):
                # try again
                return self.choose_meme_template(text)

            elif meme == 'PETER_PARKER_CRY':
                text0 = None
                text1 = text
            elif meme == 'BUT_THATS_NONE_OF_MY_BUSINESS':
                if text.endswith('?'):
                    return self.choose_meme_template(text)
                text0 = text
                text1 = "But that's none of my business"
            elif meme == 'CHANGE_MY_MIND':
                if text.endswith('?'):
                    return self.choose_meme_template(text)
            elif meme == 'BRACE_YOURSELVES_X_IS_COMING':
                text0 = "Brace yourselves"
                text1 = text
            elif meme == 'ANCIENT_ALIENS':
                if text.endswith('?'):
                    return self.choose_meme_template(text)
                text1 = "Therefore aliens"
            elif meme in ('ILL_JUST_WAIT_HERE', 'WAITING_SKELETON'):
                text1 = "I'll just wait here"
            elif meme == 'SAY_THAT_AGAIN_I_DARE_YOU':
                text1 = "Say that again I dare you"
            elif meme == 'GRUMPY_CAT':
                text1 = "No"
            elif meme == 'THAT_WOULD_BE_GREAT':
                text1 = "That would be great"
            elif meme == 'AAAAAND_ITS_GONE':
                text1 = "Aaaaand it's gone"
            elif meme == 'AND_EVERYBODY_LOSES_THEIR_MINDS':
                text1 = "Everybody loses their minds"
            elif meme == 'SEE_NOBODY_CARES':
                text1 = "See! Nobody cares"
            elif meme == 'STAR_WARS_NO':
                text1 = "Noooooooo"
            elif meme == 'MUGATU_SO_HOT_RIGHT_NOW':
                text1 = "So hot right now"

        return (meme, text0, text1)

    def make_meme(self, text):
        """
        Generate a meme with the supplied text, and return its URL.

        Meme selection logic defined in choose_meme_template().

        Return (img_url, meme_name)
        """
        meme, text0, text1 = self.choose_meme_template(text)
        meme_id = MEMES[meme]

        data = {
            'username': self.imgflip['user'],
            'password': self.imgflip['pass'],
            'template_id': meme_id,
            'text0': text0,
            'text1': text1,
        }
        try:
            r = requests.post(imgflip_url, data=data)
            img_url = r.json()['data']['url']
            return (img_url, meme)
        except (KeyError, RequestException) as e:
            logger.error(f'{e.__class__.__name__}: {e}')
            sleep(30)
            return self.make_meme(text)

    def tweet(self, status, img_url):
        "Tweet status with the image attached"
        try:
            r = requests.get(img_url)
            img = BytesIO(r.content)
            response = self.twitter.upload_media(media=img)
            media_ids = [response['media_id']]
            self.twitter.update_status(status=status, media_ids=media_ids)
        except (RequestException, TwythonError) as e:
            logger.error(f'{e.__class__.__name__}: {e}')
            raise

    def generate_meme_and_tweet(self, question):
        """
        For the given question, if it's not known:
        - generate meme
        - tweet it
        - add to database
        Return True on success, False on fail or question was known
        """
        question_title = html.unescape(question['title'])
        question_url = question['link']
        question_id = question['question_id']
        if self.db.question_is_known(question_id):
            return False
        status = f'{question_title} {question_url}'
        img_url, meme = self.make_meme(question_title)
        try:
            self.tweet(status, img_url)
            logger.info(f'Tweeted: {question_title} [{meme}]')
        except TwythonError:
            sleep(60)
            return False
        self.db.insert_question(question_id)
        return True
