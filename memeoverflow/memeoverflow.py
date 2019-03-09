from .db import MemeDatabase

import random
from time import sleep
from io import BytesIO
import html

import requests
from twython import Twython, TwythonError


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
    """
    def __init__(self, twitter, imgflip, stackexchange):
        self.db = MemeDatabase(stackexchange['site'])
        self.meme_ids = self.get_meme_ids()
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
                if self.db.select(question_id):
                    print(f'Skipping: {question}')
                    continue
                status = f'{question} {question_url}'
                img_url = self.make_meme(question)
                try:
                    self.tweet(status, img_url)
                    print(f'Tweeted: {question}')
                except TwythonError as e:
                    print(f'Failed to tweet: {e}')
                    continue
                self.db.insert(question_id)
                sleep(60*5)
            sleep(60*5)

    def get_meme_ids(self):
        """
        Return a list of meme IDs from imgflip (minus those in the blacklist)
        """
        url = 'https://api.imgflip.com/get_memes'
        memes = requests.get(url).json()
        blacklist = []
        return [m['id'] for m in memes['data']['memes']
                if m['id'] not in blacklist]

    def make_meme(self, text):
        """
        Generate a random meme with the supplied text, and return its URL
        """
        url = 'https://api.imgflip.com/caption_image'
        data = {
            'username': self.imgflip['user'],
            'password': self.imgflip['pass'],
            'template_id': random.choice(self.meme_ids),
            'text0': text,
        }
        r = requests.post(url, data=data)
        if r:
            return r.json()['data']['url']

    def get_se_questions(self, n=1):
        """
        Retreive n questions from the StackExchange site
        """
        url = 'https://api.stackexchange.com/2.2/questions'
        params = {
            'pagesize': n,
            'site': self.stackexchange['site'],
            'key': self.stackexchange.get('key', None),
        }
        r = requests.get(url, params)
        if r:
            return r.json()['items']
        else:
            print("Failed to reach StackExchange")
            return []

    def tweet(self, status, img_url):
        """
        Tweet status with the image attached
        """
        img = BytesIO(requests.get(img_url).content)
        response = self.twitter.upload_media(media=img)
        media_ids = [response['media_id']]
        self.twitter.update_status(status=status, media_ids=media_ids)
