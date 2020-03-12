import pytest
from mock import Mock, patch
from io import BytesIO
import warnings

from memeoverflow import MemeOverflow, StackExchangeNoKeyWarning
from memeoverflow.memeoverflow import _validate_keys, _validate_api_keys
from requests.exceptions import RequestException
from twython import TwythonError

from test_db import teardown_db
from vars import *


def test_validate_keys_fail():
    d = {}
    keys = ('a',)
    with pytest.raises(TypeError):
        _validate_keys('foo', d, keys)

    d = {'a': 'a_key'}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        _validate_keys('foo', d, keys)

    d = {'a': 'a_key', 'b': None}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        _validate_keys('foo', d, keys)

    d = {'a': 'a_key', 'b': 1}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        _validate_keys('foo', d, keys)

    d = {'a': 'a_key', 'b': ''}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        _validate_keys('foo', d, keys)

def test_validate_keys_pass():
    d = {'a': 'a_key'}
    keys = ('a', )
    assert _validate_keys('foo', d, keys)
    d = {'a': 'a_key', 'b': 'b_key'}
    keys = ('a', 'b')
    assert _validate_keys('foo', d, keys)

def test_validate_api_keys_fail():
    twitter = {}
    imgflip = {}
    stackexchange = {}
    with pytest.raises(TypeError):
        _validate_api_keys(twitter, imgflip, stackexchange)

    twitter = {
        'con_key': '',
        'con_sec': '',
        'acc_tok': '',
        'acc_sec': '',
    }
    imgflip = {
        'user': '',
        'pass': '',
    }
    stack_no_key = {
        'site': '',
    }
    imgflip = {}
    stackexchange = {}
    with pytest.raises(TypeError):
        _validate_api_keys(twitter, imgflip, stackexchange)

    twitter = {
        'con_key': 'a',
        'con_sec': 'a',
        'acc_tok': 'a',
        'acc_sec': 'a',
    }
    imgflip = {
        'user': 'a',
        'pass': 'a',
    }
    stackexchange = {
        'site': '',
    }
    imgflip = {}
    stackexchange = {}
    with pytest.raises(TypeError):
        _validate_api_keys(twitter, imgflip, stackexchange)

def test_validate_api_keys_pass():
    assert _validate_api_keys(fake_twitter, fake_imgflip, fake_stack_no_key)
    assert _validate_api_keys(fake_twitter, fake_imgflip, fake_stack_with_key)
    assert _validate_api_keys(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid)

def test_bad_init():
    teardown_db(test_db)
    with pytest.raises(TypeError):
        MemeOverflow()
    with pytest.raises(TypeError):
        MemeOverflow('', '', '', test_db)
    with pytest.raises(TypeError):
        MemeOverflow({}, {}, {}, test_db)
    with pytest.raises(TypeError):
        MemeOverflow(fake_twitter)
    with pytest.raises(TypeError):
        MemeOverflow(fake_twitter, fake_imgflip)
    with pytest.raises(TypeError):
        MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key)
    with pytest.raises(TypeError):
        MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid)
    teardown_db(test_db)

def test_init():
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        assert repr(mo).startswith('<MemeOverflow')
        assert repr(mo).endswith('site stackexchange>')
        assert callable(mo)
        assert mo.db.site == 'stackexchange'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_no_key(requests):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_no_key['site'],
        'key': None,
    }

    teardown_db(test_db)
    with warnings.catch_warnings(record=True) as w:
        with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key, test_db) as mo:
            assert len(w) == 1
            assert w[0].category == StackExchangeNoKeyWarning
            mock_response = Mock(json=Mock(return_value=example_se_response))
            requests.get.return_value = mock_response
            questions = mo.get_se_questions(n)
            requests.get.assert_called_once_with(stack_url, data)
            assert questions == [example_se_item_1, example_se_item_2]
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_with_key(requests):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(json=Mock(return_value=example_se_response))
        requests.get.return_value = mock_response
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        assert questions == [example_se_item_1, example_se_item_2]
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_with_key_and_userid(requests):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid, test_db) as mo:
        mock_response = Mock(json=Mock(return_value=example_se_response))
        requests.get.return_value = mock_response
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        assert questions == [example_se_item_1, example_se_item_2]
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_fail_request(requests, logger):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        requests.get.side_effect = RequestException()
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        logger.error.assert_called_once()
        assert questions == []
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_fail_bad_json(requests, logger):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(json=Mock(return_value=empty_dict))
        requests.get.return_value = mock_response
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        logger.error.assert_called_once()
        assert questions == []
    teardown_db(test_db)

def test_get_question_url_no_referral():
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        url = 'https://site.stackexchange.com/questions/98765/some-question'
        assert mo.get_question_url(url) == url
        url = 'https://customstackexchange.com/questions/98765/some-question'
        assert mo.get_question_url(url) == url

def test_get_question_url_no_referral():
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid, test_db) as mo:
        # fake_stack_with_key_and_userid['user_id'] is 12345
        url = 'https://site.stackexchange.com/questions/98765/some-question'
        referral_url = 'https://site.stackexchange.com/questions/98765/12345'
        assert mo.get_question_url(url) == referral_url
        url = 'https://customstackexchange.com/questions/98765/12345'
        referral_url = 'https://customstackexchange.com/questions/98765/12345'
        assert mo.get_question_url(url) == referral_url

@patch('memeoverflow.memeoverflow.random')
def test_choose_meme_template(random):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        # text should be on line 2 for this template
        random.choice.return_value = 'PETER_PARKER_CRY'
        meme, text0, text1 = mo.choose_meme_template('test')
        assert meme == 'PETER_PARKER_CRY'
        assert text0 is None
        assert text1 == 'test'

        # first attempt rejected due to ending in question mark
        # second attempt ok
        random.choice.return_value = None
        random.choice.side_effect = [
            'BUT_THATS_NONE_OF_MY_BUSINESS',
            'PETER_PARKER_CRY',
        ]
        meme, text0, text1 = mo.choose_meme_template('test?')
        assert meme == 'PETER_PARKER_CRY'
        assert text0 is None
        assert text1 == 'test?'

        # "is this" text should force "is this a pigeon?" template
        meme, text0, text1 = mo.choose_meme_template('is this a test?')
        assert meme == 'IS_THIS_A_PIGEON'
        assert text0 == 'is this'
        assert text1 == 'a test?'

        # text should have accompanying line 2
        random.choice.side_effect = None
        random.choice.return_value = 'SEE_NOBODY_CARES'
        meme, text0, text1 = mo.choose_meme_template('test')
        assert meme == 'SEE_NOBODY_CARES'
        assert text0 == 'test'
        assert text1 == 'See! Nobody cares'

        # try pigeon, well yes and dr evil but none match criteria, so skip
        # them all and keep trying until a no-rules one appears
        random.choice.return_value = None
        random.choice.side_effect = [
            'IS_THIS_A_PIGEON',
            'WELL_YES_BUT_ACTUALLY_NO',
            'DR_EVIL_LASER',
            'PHILOSORAPTOR',
            'BATMAN_SLAPPING_ROBIN',
        ]
        meme, text0, text1 = mo.choose_meme_template('test')
        assert meme == 'BATMAN_SLAPPING_ROBIN'
        assert text0 == 'test'
        assert text1 is None
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme(requests, random):
    data = {
        'username': 'imgflip_user',
        'password': 'imgflip_pass',
        'template_id': BATMAN_SLAPPING_ROBIN,
        'text0': 'test',
        'text1': None,
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        random.choice.return_value = 'BATMAN_SLAPPING_ROBIN'
        mock_response = Mock(json=Mock(return_value=example_imgflip_response))
        requests.post.return_value = mock_response
        img_url, meme_name = mo.make_meme('test')
        requests.post.assert_called_once_with(imgflip_url, data=data)
        assert img_url == example_imgflip_img_url
        assert meme_name == 'BATMAN_SLAPPING_ROBIN'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.sleep')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme_fail_retry(requests, random, sleep, logger):
    data = {
        'username': 'imgflip_user',
        'password': 'imgflip_pass',
        'template_id': BATMAN_SLAPPING_ROBIN,
        'text0': 'test',
        'text1': None,
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        random.choice.return_value = 'BATMAN_SLAPPING_ROBIN'
        mock_good_response = Mock(json=Mock(return_value=example_imgflip_response))
        requests.post.side_effect = [RequestException(), mock_good_response]
        img_url, meme_name = mo.make_meme('test')

        requests.post.assert_called_with(imgflip_url, data=data)
        logger.error.assert_called_once()
        assert img_url == example_imgflip_img_url
        assert meme_name == 'BATMAN_SLAPPING_ROBIN'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.sleep')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme_bad_response_retry(requests, random, sleep, logger):
    data = {
        'username': 'imgflip_user',
        'password': 'imgflip_pass',
        'template_id': BATMAN_SLAPPING_ROBIN,
        'text0': 'test',
        'text1': None,
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        random.choice.return_value = 'BATMAN_SLAPPING_ROBIN'
        mock_bad_response = Mock(json=Mock(return_value=empty_dict))
        mock_good_response = Mock(json=Mock(return_value=example_imgflip_response))
        requests.post.side_effect = [mock_bad_response, mock_good_response]
        img_url, meme_name = mo.make_meme('test')
        requests.post.assert_called_with(imgflip_url, data=data)
        logger.error.assert_called_once()
        assert img_url == example_imgflip_img_url
        assert meme_name == 'BATMAN_SLAPPING_ROBIN'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.Twython')
@patch('memeoverflow.memeoverflow.BytesIO')
def test_tweet(bytesio_class, twython_class, requests):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(content=example_imgflip_img_blob)
        requests.get.return_value = mock_response
        img_bytes = Mock()
        bytesio_class.return_value = img_bytes
        twython.upload_media.return_value = example_twitter_upload_response
        mo.tweet('test', example_imgflip_img_url)

        requests.get.assert_called_once_with(example_imgflip_img_url)
        twython.upload_media.assert_called_once_with(media=img_bytes)
        twython.update_status.assert_called_once()
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
def test_tweet_fail_imgflip(requests, logger):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        requests.get.side_effect = RequestException()
        with pytest.raises(RequestException):
            mo.tweet('test', example_imgflip_img_url)
        logger.error.assert_called_once()
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.Twython')
def test_tweet_fail_upload(twython_class, requests, logger):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(content=example_imgflip_img_blob)
        requests.get.return_value = mock_response
        twython.upload_media.side_effect = TwythonError('upload media error')
        with pytest.raises(TwythonError):
            mo.tweet('test', example_imgflip_img_url)
        logger.error.assert_called_once()
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.Twython')
def test_tweet_fail_update_status(twython_class, requests, logger):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(content=example_imgflip_img_blob)
        requests.get.return_value = mock_response
        twython.upload_media.return_value = example_twitter_upload_response
        twython.update_status.side_effect = TwythonError('update status error')
        with pytest.raises(TwythonError):
            mo.tweet('test', example_imgflip_img_url)
        logger.error.assert_called_once()
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.BytesIO')
@patch('memeoverflow.memeoverflow.Twython')
def test_generate_meme_and_tweet(twython_class, bytesio_class, requests, random, logger):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        meme = 'BATMAN_SLAPPING_ROBIN'
        random.choice.return_value = meme
        mock_imgflip_response = Mock(content=example_imgflip_img_blob)
        requests.get.return_value = mock_imgflip_response
        img_bytes = Mock()
        bytesio_class.return_value = img_bytes
        twython.upload_media.return_value = example_twitter_upload_response
        assert mo.generate_meme_and_tweet(example_question)
        question_title = example_question['title']
        log_msg = f'Tweeted: {question_title} [{meme}]'
        logger.info.assert_called_once_with(log_msg)
        assert mo.db.question_is_known(example_question['question_id'])
    teardown_db(test_db)

def test_generate_meme_and_tweet_known_question():
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mo.db.insert_question(example_question['question_id'])
        assert not mo.generate_meme_and_tweet(example_question)
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.sleep')
def test_generate_meme_and_tweet_fail(sleep):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mo.make_meme = Mock(return_value=('img_url', 'meme'))
        mo.tweet = Mock(side_effect=TwythonError('error'))
        assert not mo.generate_meme_and_tweet(example_question)
        assert not mo.db.question_is_known(example_question['question_id'])
    teardown_db(test_db)
