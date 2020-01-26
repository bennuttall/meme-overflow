from .db import MemeDatabase
from .imgflip import MEMES

import random
from time import sleep
from io import BytesIO
import html

import requests
from twython import Twython, TwythonError
from logzero import logger


class MemeOverflow:
    """
    Class for generating and tweeting memes of questions from a given
    StackExchange site

    :param dict twitter:
        Expected keys: con_key, con_sec, acc_tok, acc_sec (Twitter API keys)

    :param dict imgflip:
        Expected keys: user, pass (imgflip account)

    :param dict stackexchange:
        Expects key: site (StackExchange site name)
        Optional key: key (StackExchange API key)

    :param str db_path:
        Path to the sqlite database file
    """
    def __init__(self, twitter, imgflip, stackexchange, db_path):
        self.db = MemeDatabase(site=stackexchange['site'], db_path=db_path)
        self.twitter = Twython(
            twitter['con_key'],
            twitter['con_sec'],
            twitter['acc_tok'],
            twitter['acc_sec']
        )
        self.imgflip = imgflip
        self.stackexchange = stackexchange

    def __repr__(self):
        return f"<MemeOverflow object for site {self.stackexchange['site']}>"

    def __call__(self):
        """
        Main loop: look up questions, for each question:
        - check database
        - generate meme
        - tweet it
        - add to database
        """
        while True:
            questions = self.get_se_questions(100)
            for q in questions:
                question = html.unescape(q['title'])
                question_url = q['link']
                question_id = q['question_id']
                if self.db.question_is_known(question_id):
                    continue
                status = f'{question} {question_url}'
                img_url, meme = self.make_meme(question)
                try:
                    self.tweet(status, img_url)
                    logger.info(f'Tweeted: {question} [{meme}]')
                except TwythonError as e:
                    logger.error(f'{e.__class__.__name__}: {e}')
                    sleep(60)
                    continue
                self.db.insert_question(question_id)
                sleep(60*5)
            sleep(60*5)

    def make_meme(self, text):
        """
        Generate a random meme with the supplied text, and return its URL

        (some logic used to determine a suitable meme for the supplied text,
        see implementation for details)
        """
        url = 'https://api.imgflip.com/caption_image'
        text0 = text
        text1 = None

        if text.lower().startswith("is this "):
            meme_id = 'IS_THIS_A_PIGEON'
            text0 = "is this"
            text1 = text[8:]
        elif 'possible' in text.lower() and text.endswith('?'):
            meme = 'WELL_YES_BUT_ACTUALLY_NO'
        elif text.count('"') == 2:
            meme = 'DR_EVIL_LASER'
        else:
            meme = random.choice(list(MEMES.keys()))

        if meme in (
            'IS_THIS_A_PIGEON', 'WELL_YES_BUT_ACTUALLY_NO', 'DR_EVIL_LASER'
            ):
            # try again
            return self.make_meme(text)

        elif meme == 'PETER_PARKER_CRY':
            text0 = None
            text1 = text
        elif meme == 'BUT_THATS_NONE_OF_MY_BUSINESS':
            if text.endswith('?'):
                return self.make_meme(text)
            text0 = text
            text1 = "But that's none of my business"
        elif meme == 'CHANGE_MY_MIND':
            if text.endswith('?'):
                return self.make_meme(text)
        elif meme == 'PHILOSORAPTOR':
            if not text.endswith('?'):
                return self.make_meme(text)
        elif meme == 'BRACE_YOURSELVES_X_IS_COMING':
            text0 = "Brace yourselves"
            text1 = text
        elif meme == 'ANCIENT_ALIENS':
            if text.endswith('?'):
                return self.make_meme(text)
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
            text1 = "Everyone loses their minds"
        elif meme == 'SEE_NOBODY_CARES':
            text1 = "See! Nobody cares"
        elif meme == 'STAR_WARS_NO':
            text1 = "Noooooooo"
        elif meme == 'MUGATU_SO_HOT_RIGHT_NOW':
            text1 = "So hot right now"

        meme_id = MEMES[meme]

        data = {
            'username': self.imgflip['user'],
            'password': self.imgflip['pass'],
            'template_id': meme_id,
            'text0': text0,
            'text1': text1,
        }
        try:
            r = requests.post(url, data=data)
            img_url = r.json()['data']['url']
            return (img_url, meme)
        except Exception as e:
            logger.error(f'{e.__class__.__name__}: {e}')
            sleep(30)
            return self.make_meme(text)

    def get_se_questions(self, n=1):
        "Retreive n questions from the StackExchange site"
        url = 'https://api.stackexchange.com/2.2/questions'
        params = {
            'pagesize': n,
            'site': self.stackexchange['site'],
            'key': self.stackexchange.get('key', None),
        }
        try:
            r = requests.get(url, params)
            return r.json()['items']
        except Exception as e:
            logger.error(f'{e.__class__.__name__}: {e}')
            return []

    def tweet(self, status, img_url):
        "Tweet status with the image attached"
        try:
            r = requests.get(img_url)
            img = BytesIO(r.content)
            response = self.twitter.upload_media(media=img)
            media_ids = [response['media_id']]
            self.twitter.update_status(status=status, media_ids=media_ids)
        except Exception as e:
            logger.error(f'{e.__class__.__name__}: {e}')
