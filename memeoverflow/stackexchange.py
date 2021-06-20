import warnings
from json import JSONDecodeError

import requests
from requests.exceptions import RequestException

from .exc import StackExchangeError, StackExchangeNoKeyWarning


API_URL = 'https://api.stackexchange.com/2.2/questions'


class StackExchange:
    """
    Wrapper class for Stack Exchange API calls

    :type site: str
    :param site: Stack Exchange site name

    :type key: str or None
    :param key:
        Stack Exchange API key (optional) - if not provided, a stricter usage
        limit will apply

    :type user_id: str or None
    :param user_id:
        Stack Exchange user ID (optional) - if provided, will be used to create
        URLs with a referral code
    """
    def __init__(self, *, site, key=None, user_id=None):
        self.site = site
        self.key = key
        self.user_id = user_id

        if self.key is None:
            warnings.warn(
                "No StackExchange API key provided, limited use may apply",
                StackExchangeNoKeyWarning,
            )

    def __repr__(self):
        return f"<StackExchange site='{self.site}'>"

    def get_questions(self, n=100):
        "Retreive n questions from the StackExchange site and return as a list"
        params = {
            'pagesize': n,
            'site': self.site,
            'key': self.key,
        }
        r = requests.get(API_URL, params)
        try:
            r.raise_for_status()
            return r.json()['items']
        except (RequestException, JSONDecodeError, KeyError) as e:
            raise StackExchangeError(
                "Failed to retrieve questions from Stack Exchange"
            ) from e

    def get_question_url(self, url):
        """
        Return the URL with referral code if provided, otherwise return the
        normal link

        e.g. with referral: /questions/98765/12345
        without: /questions/98765/question-title
        """
        if self.user_id:
            return '/'.join(url.split('/')[:-1] + [str(self.user_id)])
        return url
