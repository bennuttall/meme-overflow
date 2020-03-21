from .db import MemeDatabase
from .imgflip import MEMES
from .exc import StackExchangeNoKeyWarning

import random
from time import sleep
from io import BytesIO
import html
import warnings

import requests
from json import JSONDecodeError
from twython import Twython, TwythonError
from logzero import logger


imgflip_url = 'https://api.imgflip.com/caption_image'
stack_url = 'https://api.stackexchange.com/2.2/questions'


def validate_keys(name, d, keys):
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

def validate_api_keys(twitter, imgflip, stackexchange):
    "Check all API keys are in valid format, otherwise raise TypeError."
    twitter_keys = ('con_key', 'con_sec', 'acc_tok', 'acc_sec')
    validate_keys('Twitter', twitter, twitter_keys)
    imgflip_keys = ('user', 'pass')
    validate_keys('imgflip', imgflip, imgflip_keys)
    stackexchange_keys = ('site', )
    validate_keys('Stack Exchange', stackexchange, stackexchange_keys)
    return True

def tags_to_hashtags(tags):
    """
    Replace special characters from list of tags, de-dupe and return string of
    hashtags.

    e.g. tags_to_hashtags(['foo', 'bar', 'foobar', 'foo-bar'])
         => '#foo #bar #foobar'
    """
    hashtags = set()
    for tag in tags:
        hashtag = tag.replace('-', '').replace('.', '')
        try:
            int(hashtag)
        except ValueError:
            hashtags.add(f'#{hashtag}')
    return ' '.join(hashtags)


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
        Optional keys: key, user_id (Stack Exchange API key & user ID)

    :param str db_path:
        Path to the sqlite database file
    """
    def __init__(self, twitter, imgflip, stackexchange, db_path):
        validate_api_keys(twitter, imgflip, stackexchange)

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

        try:
            self.stackexchange_user = str(stackexchange['user_id'])
        except KeyError:
            self.stackexchange_user = None

    def __repr__(self):
        return f"<MemeOverflow object for site {self.stackexchange['site']}>"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self):
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
        Retreive n questions from the StackExchange site and return as a list.
        Note: filters out known questions.
        """
        params = {
            'pagesize': n,
            'site': self.stackexchange['site'],
            'key': self.stackexchange.get('key', None),
        }
        r = requests.get(stack_url, params)
        if r.status_code == 200:
            try:
                # filter out known questions
                new_questions = [
                    q
                    for q in r.json()['items']
                    if not self.db.question_is_known(q['question_id'])
                ]
                logger.info(f'{len(new_questions)} new questions')
                return new_questions
            except (JSONDecodeError, KeyError) as e:
                logger.error(f'{e.__class__.__name__}: {e}')
        else:
            try:
                error = r.json()['error_message']
                logger.error(f'Unable to connect to Stack Exchage: status code {r.status_code} - {error}')
            except (JSONDecodeError, KeyError):
                logger.error(f'Unable to connect to Stack Exchage: status code {r.status_code}')

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
        r = requests.post(imgflip_url, data=data)
        if r.status_code == 200:
            try:
                img_url = r.json()['data']['url']
                return (img_url, meme)
            except (JSONDecodeError, KeyError) as e:
                logger.error(f'{e.__class__.__name__}: {e}')
        else:
            logger.error(f'Unable to connect to imgflip: status code {r.status_code}')
        sleep(60)
        return self.make_meme(text)

    def tweet(self, status, img_url):
        "Tweet status with the image attached"
        r = requests.get(img_url)
        if r.status_code == 200:
            img = BytesIO(r.content)
            try:
                response = self.twitter.upload_media(media=img)
                media_ids = [response['media_id']]
                self.twitter.update_status(status=status, media_ids=media_ids)
            except TwythonError as e:
                logger.error(f'{e.__class__.__name__}: {e}')
                raise
        else:
            logger.error(f'Unable to connect to imgflip: status code {r.status_code}')

    def get_question_url(self, url):
        """
        Return the URL with referral code if provided, otherwise return the
        normal link

        e.g. with referral: /questions/98765/12345
        without: /questions/98765/question-title
        """
        if self.stackexchange_user:
            return '/'.join(url.split('/')[:-1] + [self.stackexchange_user])
        else:
            return url

    def generate_meme_and_tweet(self, question):
        """
        For the given question, if it's not known:
        - generate meme
        - tweet it
        - add to database
        Return True on success, False on fail or question was known
        """
        question_title = html.unescape(question['title'])
        question_url = self.get_question_url(question['link'])
        question_id = question['question_id']
        tags = tags_to_hashtags(question['tags'])
        status = f'{question_title} {question_url} {tags}'
        if len(status) > 240:
            status = f'{question_title} {question_url}'
            logger.info('Tweet too long - removing tags')
        img_url, meme = self.make_meme(question_title)
        try:
            self.tweet(status, img_url)
            logger.info(f'Tweeted: {question_title} [{meme}]')
        except TwythonError:
            return False
        self.db.insert_question(question_id)
        return True
