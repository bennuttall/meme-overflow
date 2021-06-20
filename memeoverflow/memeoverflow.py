import random
from time import sleep
import html
import copy

from logzero import logger
from requests.exceptions import RequestException

from .stackexchange import StackExchange
from .db import MemeDatabase
from .imgflip import ImgFlip, MEMES
from .twitter import Twitter
from .utils import tags_to_hashtags, download_image_bytes
from .exc import ImgFlipError, TwitterError, StackExchangeError


class MemeOverflow:
    """
    Class for generating and tweeting memes of questions from a given
    StackExchange site

    :type twitter: dict
    :param twitter:
        Expected keys: con_key, con_sec, acc_tok, acc_sec (Twitter API keys)

    :type imgflip: dict
    :param imgflip:
        Expected keys: user, pass (imgflip account)

    :type stackexchange: dict
    :param stackexchange:
        Expected key: site (Stack Exchange site name)
        Optional keys: key, user_id (Stack Exchange API key & User ID)

    :type db_path: str
    :param db_path:
        Path to the sqlite database file
    """
    def __init__(self, twitter, imgflip, stackexchange, db_path):
        self.site = stackexchange['site']
        self.stackexchange = StackExchange(**stackexchange)
        self.imgflip = ImgFlip(**imgflip)
        self.twitter = Twitter(**twitter)
        self.db = MemeDatabase(site=self.site, db_path=db_path)

    def __repr__(self):
        return f"<MemeOverflow site='{self.site}'>"

    def __call__(self):
        """
        Main loop - get questions, make memes and tweet them, with sensible
        pauses
        """
        questions = self.get_se_questions()
        if questions:
            for q in questions:
                tweeted = self.generate_meme_and_tweet(q)
                if tweeted:
                    sleep(60*5)
                else:
                    sleep(60)
        else:
            sleep(60*5)

    def get_se_questions(self, n=100):
        """
        Retreive n questions from the StackExchange site and return as a list,
        filtering out any known questions.
        """
        try:
            questions = self.stackexchange.get_questions(n=n)
        except StackExchangeError as e:
            logger.exception(e)
            return
        return [
            q
            for q in questions
            if not self.db.question_is_known(q['question_id'])
        ]

    def choose_meme_template(self, text):
        """
        Choose a meme for the supplied text. If the text fits one of the
        templates well, it will use that one, otherwise it will be random. If
        text does not work with randomly chosen template, this method will be
        called again. Some templates move text to the second row or add their
        own second row of text to complete the meme.

        Return (meme_name, text_parts)
        """
        if text.lower().startswith("is this "):
            meme = 'IS_THIS_A_PIGEON'
            text = text[8:]
        elif 'possible' in text.lower() and text.endswith('?'):
            meme = 'WELL_YES_BUT_ACTUALLY_NO'
        elif text.count('"') == 2:
            meme = 'DR_EVIL_LASER'
        elif text.lower().startswith('if') and text.endswith('?'):
            meme = 'PHILOSORAPTOR'
        else:
            # don't allow these to be picked at random
            special_memes = {
                'IS_THIS_A_PIGEON',
                'WELL_YES_BUT_ACTUALLY_NO',
                'DR_EVIL_LASER',
                'PHILOSORAPTOR',
            }
            if text.endswith('?'):
                special_memes |= {
                    'BUT_THATS_NONE_OF_MY_BUSINESS',
                    'CHANGE_MY_MIND',
                    'ANCIENT_ALIENS',
                    'AND_EVERYBODY_LOSES_THEIR_MINDS',
                }
            else:
                special_memes |= {
                    'GRUMPY_CAT',
                }
            meme = random.choice(list(set(MEMES.keys()) - special_memes))

        text_parts = self.place_text(meme, text)

        return (meme, text_parts)

    def place_text(self, meme, text):
        """
        Decide where the given text should go on the given meme template, including any
        template-specific text. Return a 2-tuple of strings.
        """
        meme_dict = copy.deepcopy(MEMES[meme])
        text_location = meme_dict['text_location']
        meme_dict[text_location] = text

        return (meme_dict['text0'], meme_dict['text1'])

    def generate_meme_and_tweet(self, question):
        """
        For the given question, if it's not known:
        - generate meme
        - tweet it
        - add to database
        Return True on success, False on fail or question was known
        """
        question_title = html.unescape(question['title'])
        question_url = self.stackexchange.get_question_url(question['link'])
        question_id = question['question_id']
        tags = tags_to_hashtags(question['tags'])
        status = f"{question_title} {question_url} {tags}"

        if len(status) > 240:
            status = f"{question_title} {question_url}"
            logger.info("Tweet too long - removing tags")
        meme, text_parts = self.choose_meme_template(question_title)
        try:
            img_url = self.imgflip.make_meme(meme=meme, text_parts=text_parts)
        except ImgFlipError as e:
            logger.exception(e)
            return False

        try:
            img_bytes = download_image_bytes(img_url)
        except RequestException:
            logger.exception("Failed to download image")
            return False

        try:
            self.twitter.tweet_with_image(status, img_bytes)
            logger.info(f"Tweeted: {question_title} [{meme}]")
        except TwitterError:
            logger.exception(e)
            return False

        self.db.insert_question(question_id)
        return True
