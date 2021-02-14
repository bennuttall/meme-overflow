import pytest
from mock import Mock, patch, call
from io import BytesIO
import warnings
from itertools import cycle

from memeoverflow import MemeOverflow, StackExchangeNoKeyWarning
from memeoverflow.memeoverflow import (
    validate_keys, validate_api_keys, tags_to_hashtags
)
from twython import TwythonError

from test_db import teardown_db


def test_validate_keys_fail():
    d = {}
    keys = ('a',)
    with pytest.raises(TypeError):
        validate_keys('foo', d, keys)

    d = {'a': 'a_key'}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        validate_keys('foo', d, keys)

    d = {'a': 'a_key', 'b': None}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        validate_keys('foo', d, keys)

    d = {'a': 'a_key', 'b': 1}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        validate_keys('foo', d, keys)

    d = {'a': 'a_key', 'b': ''}
    keys = ('a', 'b')
    with pytest.raises(TypeError):
        validate_keys('foo', d, keys)

def test_validate_keys_pass():
    d = {'a': 'a_key'}
    keys = ('a', )
    assert validate_keys('foo', d, keys)
    d = {'a': 'a_key', 'b': 'b_key'}
    keys = ('a', 'b')
    assert validate_keys('foo', d, keys)

def test_validate_api_keys_fail():
    twitter = {}
    imgflip = {}
    stackexchange = {}
    with pytest.raises(TypeError):
        validate_api_keys(twitter, imgflip, stackexchange)

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
        validate_api_keys(twitter, imgflip, stackexchange)

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
        validate_api_keys(twitter, imgflip, stackexchange)

def test_validate_api_keys_pass(fake_twitter, fake_imgflip, fake_stack_no_key, fake_stack_with_key, fake_stack_with_key_and_userid):
    assert validate_api_keys(fake_twitter, fake_imgflip, fake_stack_no_key)
    assert validate_api_keys(fake_twitter, fake_imgflip, fake_stack_with_key)
    assert validate_api_keys(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid)

def test_tags_to_hashtags():
    tags = []
    assert tags_to_hashtags(tags) == ''

    tags = ['1']
    assert tags_to_hashtags(tags) == ''

    tags = ['1', '10', '100']
    assert tags_to_hashtags(tags) == ''

    tags = ['a']
    assert tags_to_hashtags(tags) == '#a'

    tags = ['1a', 'a10', '100']
    hashtags = tags_to_hashtags(tags)
    assert set(hashtags.split()) == {'#1a', '#a10'}

    tags = ['foo-bar']
    assert tags_to_hashtags(tags) == '#foobar'

    tags = ['foo.bar']
    assert tags_to_hashtags(tags) == '#foobar'

    tags = ['a', 'b']
    hashtags = tags_to_hashtags(tags)
    assert set(hashtags.split()) == {'#a', '#b'}

    tags = ['100', 'a', 'b']
    hashtags = tags_to_hashtags(tags)
    assert set(hashtags.split()) == {'#a', '#b'}

    tags = ['foo', 'bar', 'foobar']
    hashtags = tags_to_hashtags(tags)
    assert set(hashtags.split()) == {'#foo', '#bar', '#foobar'}

    tags = ['c', 'c#', 'c#8', 'c++', 'c++11', '.net']
    hashtags = tags_to_hashtags(tags)
    assert set(hashtags.split()) == {
        '#c', '#csharp', '#csharp8', '#cpp', '#cpp11', '#dotnet',
    }

    tags = ['python', 'python2x', 'python3x']
    hashtags = tags_to_hashtags(tags)
    assert set(hashtags.split()) == {'#python', '#python2', '#python3'}

def test_bad_init(test_db, fake_twitter, fake_imgflip, fake_stack_with_key, fake_stack_with_key_and_userid):
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

def test_init(fake_twitter, fake_imgflip, fake_stack_with_key, test_db):
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        assert repr(mo).startswith('<MemeOverflow')
        assert repr(mo).endswith('site stackexchange>')
        assert callable(mo)
        assert mo.db.site == 'stackexchange'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_no_key(requests, test_db, fake_twitter, fake_imgflip, fake_stack_no_key, example_se_response, stack_url, example_se_item_1, example_se_item_2):
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
            mock_response = Mock(
                json=Mock(return_value=example_se_response),
                status_code=200
            )
            requests.get.return_value = mock_response
            questions = mo.get_se_questions(n)
            requests.get.assert_called_once_with(stack_url, data)
            assert questions == [example_se_item_1, example_se_item_2]
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_with_key(requests, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_se_response, stack_url, example_se_item_1, example_se_item_2):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(
            json=Mock(return_value=example_se_response),
            status_code=200,
        )
        requests.get.return_value = mock_response
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        assert questions == [example_se_item_1, example_se_item_2]
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_with_key_and_userid(requests, fake_twitter, fake_imgflip, fake_stack_with_key, fake_stack_with_key_and_userid, test_db, example_se_response, stack_url, example_se_item_1, example_se_item_2):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid, test_db) as mo:
        mock_response = Mock(
            json=Mock(return_value=example_se_response),
            status_code=200,
        )
        requests.get.return_value = mock_response
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        assert questions == [example_se_item_1, example_se_item_2]
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_fail_request(requests, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, stack_url):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        requests.get.return_value = Mock(
            status_code=400,
            json=Mock(return_value={'error_message': 'error'}),
        )
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        logger.error.assert_called_once()
        assert questions is None
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_bad_request(requests, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, stack_url):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        requests.get.return_value = Mock(
            status_code=400,
            json=Mock(return_value={'error_message': 'error'}),
        )
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        logger.error.assert_called_once()
        assert questions is None
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
def test_get_se_questions_fail_bad_json(requests, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, stack_url, empty_dict):
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_with_key['site'],
        'key': fake_stack_with_key['key'],
    }

    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(
            status_code=200,
            json=Mock(return_value=empty_dict),
        )
        requests.get.return_value = mock_response
        questions = mo.get_se_questions(n)
        requests.get.assert_called_once_with(stack_url, data)
        logger.error.assert_called_once()
        assert questions is None
    teardown_db(test_db)

def test_get_question_url_no_referral(fake_twitter, fake_imgflip, fake_stack_with_key, test_db):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        url = 'https://site.stackexchange.com/questions/98765/some-question'
        assert mo.get_question_url(url) == url
        url = 'https://customstackexchange.com/questions/98765/some-question'
        assert mo.get_question_url(url) == url
    teardown_db(test_db)

def test_get_question_url_with_referral(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid, test_db):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key_and_userid, test_db) as mo:
        # fake_stack_with_key_and_userid['user_id'] is 12345
        url = 'https://site.stackexchange.com/questions/98765/some-question'
        referral_url = 'https://site.stackexchange.com/questions/98765/12345'
        assert mo.get_question_url(url) == referral_url
        url = 'https://customstackexchange.com/questions/98765/12345'
        referral_url = 'https://customstackexchange.com/questions/98765/12345'
        assert mo.get_question_url(url) == referral_url
    teardown_db(test_db)

def assert_meme_choice(random, mo, text, random_memes, chosen_meme,
                       expected_text0, expected_text1):
    random.choice.side_effect = random_memes
    meme, text0, text1 = mo.choose_meme_template(text)
    assert meme == chosen_meme
    assert text0 == expected_text0
    assert text1 == expected_text1

@patch('memeoverflow.memeoverflow.random')
def test_choose_meme_template(random, fake_twitter, fake_imgflip, fake_stack_with_key, test_db):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        # text should be on line 2 for this template
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['PETER_PARKER_CRY'],
            chosen_meme='PETER_PARKER_CRY',
            expected_text0=None,
            expected_text1='test'
        )

        # first attempt rejected due to ending in question mark
        # second attempt ok
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test?',
            random_memes=['BUT_THATS_NONE_OF_MY_BUSINESS', 'PETER_PARKER_CRY'],
            chosen_meme='PETER_PARKER_CRY',
            expected_text0=None,
            expected_text1='test?'
        )

        # "is this" text should force "is this a pigeon?" template
        assert_meme_choice(
            mo=mo,
            random=random,
            text='is this a test?',
            random_memes=['PETER_PARKER_CRY'],
            chosen_meme='IS_THIS_A_PIGEON',
            expected_text0='is this',
            expected_text1='a test?'
        )

        # text should have accompanying line 2
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['SEE_NOBODY_CARES'],
            chosen_meme='SEE_NOBODY_CARES',
            expected_text0='test',
            expected_text1='See! Nobody cares'
        )

        # word "possible" trigger
        assert_meme_choice(
            mo=mo,
            random=random,
            text='is it possible this is a test?',
            random_memes=['SEE_NOBODY_CARES'],
            chosen_meme='WELL_YES_BUT_ACTUALLY_NO',
            expected_text0='is it possible this is a test?',
            expected_text1=None
        )

        # quotes => dr evil
        assert_meme_choice(
            mo=mo,
            random=random,
            text='what is "this" test',
            random_memes=['SEE_NOBODY_CARES'],
            chosen_meme='DR_EVIL_LASER',
            expected_text0='what is "this" test',
            expected_text1=None
        )

        # if question => philosoraptor
        assert_meme_choice(
            mo=mo,
            random=random,
            text='if this is a test?',
            random_memes=['SEE_NOBODY_CARES'],
            chosen_meme='PHILOSORAPTOR',
            expected_text0='if this is a test?',
            expected_text1=None
        )

        # doesn't end in ? so can be none of my business
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['BUT_THATS_NONE_OF_MY_BUSINESS'],
            chosen_meme='BUT_THATS_NONE_OF_MY_BUSINESS',
            expected_text0='test',
            expected_text1="But that's none of my business"
        )

        # doesn't end in ? so can be change my mind
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['CHANGE_MY_MIND'],
            chosen_meme='CHANGE_MY_MIND',
            expected_text0='test',
            expected_text1=None
        )

        # doesn't end in ? so can be ancient aliens
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['ANCIENT_ALIENS'],
            chosen_meme='ANCIENT_ALIENS',
            expected_text0='test',
            expected_text1='Therefore aliens'
        )

        # ends in ? can't be any of these
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test?',
            random_memes=[
                'BUT_THATS_NONE_OF_MY_BUSINESS',
                'CHANGE_MY_MIND',
                'ANCIENT_ALIENS',
                'BATMAN_SLAPPING_ROBIN',
            ],
            chosen_meme='BATMAN_SLAPPING_ROBIN',
            expected_text0='test?',
            expected_text1=None
        )

        # brace yourselves
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['BRACE_YOURSELVES_X_IS_COMING'],
            chosen_meme='BRACE_YOURSELVES_X_IS_COMING',
            expected_text0='Brace yourselves',
            expected_text1='test'
        )

        # i'll just wait here
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['ILL_JUST_WAIT_HERE'],
            chosen_meme='ILL_JUST_WAIT_HERE',
            expected_text0='test',
            expected_text1="I'll just wait here"
        )

        # say that again
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['SAY_THAT_AGAIN_I_DARE_YOU'],
            chosen_meme='SAY_THAT_AGAIN_I_DARE_YOU',
            expected_text0='test',
            expected_text1="Say that again I dare you"
        )

        # grumpy cat
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['GRUMPY_CAT'],
            chosen_meme='GRUMPY_CAT',
            expected_text0='test',
            expected_text1="No"
        )

        # that would be great
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['THAT_WOULD_BE_GREAT'],
            chosen_meme='THAT_WOULD_BE_GREAT',
            expected_text0='test',
            expected_text1="That would be great"
        )

        # and it's gone
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['AAAAAND_ITS_GONE'],
            chosen_meme='AAAAAND_ITS_GONE',
            expected_text0='test',
            expected_text1="Aaaaand it's gone"
        )

        # AND_EVERYBODY_LOSES_THEIR_MINDS
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['AND_EVERYBODY_LOSES_THEIR_MINDS'],
            chosen_meme='AND_EVERYBODY_LOSES_THEIR_MINDS',
            expected_text0='test',
            expected_text1="Everybody loses their minds"
        )

        # STAR_WARS_NO
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['STAR_WARS_NO'],
            chosen_meme='STAR_WARS_NO',
            expected_text0='test',
            expected_text1="Noooooooo"
        )

        # MUGATU_SO_HOT_RIGHT_NOW
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['MUGATU_SO_HOT_RIGHT_NOW'],
            chosen_meme='MUGATU_SO_HOT_RIGHT_NOW',
            expected_text0='test',
            expected_text1="So hot right now"
        )

        # BIKE_FALL
        assert_meme_choice(
            mo=mo,
            random=random,
            text='test',
            random_memes=['BIKE_FALL'],
            chosen_meme='BIKE_FALL',
            expected_text0=None,
            expected_text1="test"
        )
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme(requests, random, BATMAN_SLAPPING_ROBIN, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_response, example_imgflip_img_blob, imgflip_url, example_imgflip_img_url):
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
        mock_imgflip_post_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.return_value = mock_imgflip_post_response
        mock_imgflip_get_response = Mock(
            status_code=200,
            content=example_imgflip_img_blob,
        )
        requests.get.return_value = mock_imgflip_get_response
        img_url, meme_name = mo.make_meme('test')
        requests.post.assert_called_once_with(imgflip_url, data=data)
        assert img_url == example_imgflip_img_url
        assert meme_name == 'BATMAN_SLAPPING_ROBIN'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.sleep')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme_fail_retry(requests, random, sleep, logger, BATMAN_SLAPPING_ROBIN, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_response, imgflip_url, example_imgflip_img_url):
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
        mock_bad_response = Mock(status_code=400)
        mock_good_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.side_effect = [mock_bad_response, mock_good_response]
        img_url, meme_name = mo.make_meme('test')

        requests.post.assert_called_with(imgflip_url, data=data)
        logger.error.assert_called_once()
        sleep.assert_called_once()
        assert img_url == example_imgflip_img_url
        assert meme_name == 'BATMAN_SLAPPING_ROBIN'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.sleep')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme_fail_keyerror_retry(requests, random, sleep, logger, BATMAN_SLAPPING_ROBIN, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, empty_dict, example_imgflip_response, imgflip_url, example_imgflip_img_url):
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
        mock_bad_response = Mock(
            status_code=200,
            json=Mock(return_value=empty_dict),
        )
        mock_good_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.side_effect = [mock_bad_response, mock_good_response]
        img_url, meme_name = mo.make_meme('test')

        requests.post.assert_called_with(imgflip_url, data=data)
        logger.error.assert_called_once()
        sleep.assert_called_once()
        assert img_url == example_imgflip_img_url
        assert meme_name == 'BATMAN_SLAPPING_ROBIN'
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.sleep')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
def test_make_meme_bad_response_retry(requests, random, sleep, logger, BATMAN_SLAPPING_ROBIN, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_response, empty_dict, imgflip_url, example_imgflip_img_url):
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
        mock_good_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
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
def test_tweet(bytesio_class, twython_class, requests, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_img_blob, example_twitter_upload_response, example_imgflip_img_url):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(
            json=Mock(return_value=example_imgflip_img_blob),
            status_code=200,
        )
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
def test_tweet_fail_imgflip(requests, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_img_url):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        requests.get.return_value = Mock(status_code=400)
        mo.tweet('test', example_imgflip_img_url)
        logger.error.assert_called_once()
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.Twython')
def test_tweet_fail_upload(twython_class, requests, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_img_blob, example_imgflip_img_url):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(status_code=200, content=example_imgflip_img_blob)
        requests.get.return_value = mock_response
        twython.upload_media.side_effect = TwythonError('upload media error')
        with pytest.raises(TwythonError):
            mo.tweet('test', example_imgflip_img_url)
        logger.error.assert_called_once()
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.Twython')
def test_tweet_fail_update_status(twython_class, requests, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_img_blob, example_twitter_upload_response, example_imgflip_img_url):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_response = Mock(status_code=200, content=example_imgflip_img_blob)
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
def test_generate_meme_and_tweet(twython_class, bytesio_class, requests, random, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_response, example_imgflip_img_blob, example_twitter_upload_response, example_question):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        meme = 'BATMAN_SLAPPING_ROBIN'
        random.choice.return_value = meme
        mock_imgflip_post_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.return_value = mock_imgflip_post_response
        mock_imgflip_get_response = Mock(
            status_code=200,
            content=example_imgflip_img_blob,
        )
        requests.get.return_value = mock_imgflip_get_response
        img_bytes = Mock()
        bytesio_class.return_value = img_bytes
        twython.upload_media.return_value = example_twitter_upload_response
        assert mo.generate_meme_and_tweet(example_question)
        question_title = example_question['title']
        log_msg = f'Tweeted: {question_title} [{meme}]'
        logger.info.assert_called_once_with(log_msg)
        assert mo.db.question_is_known(example_question['question_id'])
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.BytesIO')
@patch('memeoverflow.memeoverflow.Twython')
def test_generate_meme_and_tweet_long_question(twython_class, bytesio_class, requests, random, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_imgflip_response, example_imgflip_img_blob, example_twitter_upload_response, example_long_question, example_question):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        meme = 'BATMAN_SLAPPING_ROBIN'
        random.choice.return_value = meme
        mock_imgflip_post_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.return_value = mock_imgflip_post_response
        mock_imgflip_get_response = Mock(
            status_code=200,
            content=example_imgflip_img_blob,
        )
        requests.get.return_value = mock_imgflip_get_response
        img_bytes = Mock()
        bytesio_class.return_value = img_bytes
        twython.upload_media.return_value = example_twitter_upload_response
        assert mo.generate_meme_and_tweet(example_long_question)
        question_title = example_long_question['title']
        log_msg_1 = 'Tweet too long - removing tags'
        log_msg_2 = f'Tweeted: {question_title} [{meme}]'
        calls = [call(log_msg_1), call(log_msg_2)]
        logger.info.assert_has_calls(calls)
        assert mo.db.question_is_known(example_question['question_id'])
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.sleep')
def test_generate_meme_and_tweet_fail(sleep, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_question):
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mo.make_meme = Mock(return_value=('img_url', 'meme'))
        mo.tweet = Mock(side_effect=TwythonError('error'))
        assert not mo.generate_meme_and_tweet(example_question)
        assert not mo.db.question_is_known(example_question['question_id'])
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.BytesIO')
@patch('memeoverflow.memeoverflow.Twython')
@patch('memeoverflow.memeoverflow.sleep')
def test_call(sleep, twython_class, bytesio_class, requests, random, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_se_response, example_imgflip_img_blob, example_imgflip_response, example_twitter_upload_response):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_se_response = Mock(
            status_code=200,
            json=Mock(return_value=example_se_response),
        )
        mock_imgflip_response = Mock(
            status_code=200,
            content=example_imgflip_img_blob,
        )
        requests.get.side_effect = cycle(
            [mock_se_response, mock_imgflip_response]
        )
        mock_imgflip_post_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.return_value = mock_imgflip_post_response
        meme = 'BATMAN_SLAPPING_ROBIN'
        random.choice.return_value = meme
        mock_imgflip_response = Mock(
            status_code=200,
            content=example_imgflip_img_blob,
        )
        requests.get.return_value = mock_imgflip_response
        img_bytes = Mock()
        bytesio_class.return_value = img_bytes
        twython.upload_media.return_value = example_twitter_upload_response
        mo()
        logger.error.assert_not_called()
        assert twython.update_status.call_count == 2
        assert sleep.call_count == 2
    teardown_db(test_db)

@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.sleep')
def test_call_no_questions(sleep, requests, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, empty_dict):
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_se_response = Mock(
            status_code=400,
            json=Mock(return_value=empty_dict)
        )
        requests.get.return_value = mock_se_response
        mo()
        assert sleep.call_count == 1

@patch('memeoverflow.memeoverflow.logger')
@patch('memeoverflow.memeoverflow.random')
@patch('memeoverflow.memeoverflow.requests')
@patch('memeoverflow.memeoverflow.BytesIO')
@patch('memeoverflow.memeoverflow.Twython')
@patch('memeoverflow.memeoverflow.sleep')
def test_call_fail(sleep, twython_class, bytesio_class, requests, random, logger, fake_twitter, fake_imgflip, fake_stack_with_key, test_db, example_se_response, example_imgflip_img_blob, example_imgflip_response, example_twitter_upload_response):
    twython = Mock()
    twython_class.return_value = twython
    teardown_db(test_db)
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_with_key, test_db) as mo:
        mock_se_response = Mock(
            status_code=200,
            json=Mock(return_value=example_se_response),
        )
        mock_imgflip_get_response = Mock(
            status_code=200,
            content=example_imgflip_img_blob,
        )
        requests.get.side_effect = cycle([mock_se_response, mock_imgflip_get_response])
        mock_imgflip_post_response = Mock(
            status_code=200,
            json=Mock(return_value=example_imgflip_response),
        )
        requests.post.return_value = mock_imgflip_post_response
        meme = 'BATMAN_SLAPPING_ROBIN'
        random.choice.return_value = meme
        mock_imgflip_response = Mock(content=example_imgflip_img_blob)
        requests.get.return_value = mock_imgflip_response
        img_bytes = Mock()
        bytesio_class.return_value = img_bytes
        twython.upload_media.return_value = example_twitter_upload_response
        twython.update_status.side_effect = TwythonError('update status error')
        mo()
        assert twython.update_status.call_count == 2
        assert sleep.call_count == 2
    teardown_db(test_db)
