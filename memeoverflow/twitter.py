from twython import Twython, TwythonError

from .exc import TwitterError


class Twitter:
    """
    Wrapper class for Twitter API calls

    :type con_key: str
    :param con_key: Twitter API consumer key

    :type con_sec: str
    :param con_sec: Twitter API consumer secret

    :type acc_key: str
    :param acc_key: Twitter API access key

    :type acc_sec: str
    :param acc_sec: Twitter API access secret
    """
    def __init__(self, con_key, con_sec, acc_tok, acc_sec):
        self.twython = Twython(con_key, con_sec, acc_tok, acc_sec)

    def __repr__(self):
        return "<Twitter>"

    def tweet_with_image(self, status, img_bytes):
        "Tweet status with the image attached"
        try:
            response = self.twython.upload_media(media=img_bytes)
            media_ids = [response['media_id']]
            self.twython.update_status(status=status, media_ids=media_ids)
        except TwythonError as e:
            raise TwitterError from e
