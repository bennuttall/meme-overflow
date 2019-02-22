from db import MemeDatabase

import requests
import random
from time import sleep
from io import BytesIO
import html

from twython import Twython, TwythonError


class MemeGenerator:
    def __init__(self, twitter, imgflip, stackexchange):
        self.db = MemeDatabase(stackexchange)
        self.meme_ids = self.get_meme_ids()
        self.twitter = Twython(
            twitter['con_key'],
            twitter['con_sec'],
            twitter['acc_tok'],
            twitter['acc_sec']
        )
        self.imgflip = imgflip
        self.stackexchange = stackexchange
        self.main()

    def get_meme_ids(self):
        url = 'https://api.imgflip.com/get_memes'
        memes = requests.get(url).json()
        return [m['id'] for m in memes['data']['memes']]

    def make_meme(self, text):
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
        url = 'https://api.stackexchange.com/2.2/questions'
        params = {
            'pagesize': n,
            'site': self.stackexchange
        }
        r = requests.get(url, params)
        if r:
            return r.json()['items']

    def tweet(self, status, img_url):
        img = BytesIO(requests.get(img_url).content)
        response = self.twitter.upload_media(media=img)
        media_ids = [response['media_id']]
        self.twitter.update_status(status=status, media_ids=media_ids)

    def main(self):
        while True:
            questions = self.get_se_questions(100)
            for q in questions:
                question = html.unescape(q['title'])
                question_url = q['link']
                if self.db.select(question_url):
                    print(f'Skipping: {question}')
                    continue
                status = f'{question} {question_url}'
                img_url = self.make_meme(question)
                try:
                    self.tweet(status, img_url)
                    print(f'Tweeted: {question}')
                except TwythonError:
                    print(f'Failed to tweet: {question}')
                    continue
                self.db.insert(question_url)
                sleep(60)
            sleep(60)
