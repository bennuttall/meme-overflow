import pytest
from mock import Mock, patch

from memeoverflow import MemeOverflow
from requests.exceptions import ConnectionError

from test_db import teardown_db


test_db = 'test_memes.db'
fake_twitter = {
    'con_key': 'tw_con_key',
    'con_sec': 'tw_con_sec',
    'acc_tok': 'tw_acc_tok',
    'acc_sec': 'tw_acc_sec',
}
fake_imgflip = {
    'user': 'imgflip_user',
    'pass': 'imgflip_pass',
}
fake_stack_no_key = {
    'site': 'stackexchange',
}
fake_stack_no_key_with_key = {
    'site': 'stackexchange',
    'key': 'stack_key',
}

example_se_item_1 = {
    'tags': ['tag', 'another-tag'],
    'question_id': 123456,
    'link': 'https://stackexchange.stackexchange.com/questions/123456/some-question',
    'title': 'Some question'
}
example_se_item_2 = {
    'tags': ['tag', 'another-tag'],
    'question_id': 123457,
    'link': 'https://stackexchange.stackexchange.com/questions/123457/anther-question',
    'title': 'Another question'
}
example_se_response = {
    'items': [example_se_item_1, example_se_item_2],
    'has_more': True,
    'quota_max': 300,
    'quota_remaining': 299,
}

example_imgflip_img_url = 'https://i.imgflip.com/test.jpg'

example_imgflip_response = {
    'success': True,
    'data': {
        'url': example_imgflip_img_url,
        'page_url': 'https://imgflip.com/i/test'
    }
}

stack_url = 'https://api.stackexchange.com/2.2/questions'
imgflip_url = 'https://api.imgflip.com/caption_image'

BATMAN_SLAPPING_ROBIN = 438680


def test_mo_bad_init():
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
        MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key)

def test_mo_init():
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key, test_db) as mo:
        assert repr(mo).startswith('<MemeOverflow')
        assert repr(mo).endswith('site stackexchange>')
        assert callable(mo)
        assert mo.db.site == 'stackexchange'
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key_with_key, test_db) as mo:
        assert repr(mo).startswith('<MemeOverflow')
        assert repr(mo).endswith('site stackexchange>')
        assert callable(mo)
        assert mo.db.site == 'stackexchange'

def test_mo_get_se_questions():
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_no_key['site'],
        'key': None,
    }

    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key, test_db) as mo:
        with patch('memeoverflow.memeoverflow.requests') as requests:
            mock_response = Mock(json=Mock(return_value=example_se_response))
            requests.get.return_value = mock_response
            questions = mo.get_se_questions(n)
            requests.get.assert_called_once_with(stack_url, data)
            assert questions == [example_se_item_1, example_se_item_2]

    data = {
        'pagesize': n,
        'site': fake_stack_no_key_with_key['site'],
        'key': fake_stack_no_key_with_key['key'],
    }

    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key_with_key, test_db) as mo:
        with patch('memeoverflow.memeoverflow.requests') as requests:
            mock_response = Mock(json=Mock(return_value=example_se_response))
            requests.get.return_value = mock_response
            questions = mo.get_se_questions(n)
            requests.get.assert_called_once_with(stack_url, data)
            assert questions == [example_se_item_1, example_se_item_2]

def test_mo_get_se_questions_fail():
    n = 2
    data = {
        'pagesize': n,
        'site': fake_stack_no_key_with_key['site'],
        'key': fake_stack_no_key_with_key['key'],
    }

    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key_with_key, test_db) as mo:
        with patch('memeoverflow.memeoverflow.requests') as requests:
            with patch('memeoverflow.memeoverflow.logger') as logger:
                mock_response = Mock(json=Mock(return_value=example_se_response))
                requests.get.side_effect = ConnectionError()
                questions = mo.get_se_questions(n)
                requests.get.assert_called_once_with(stack_url, data)
                logger.error.assert_called_once()
                assert questions == []

def test_mo_choose_meme_template():
    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key, test_db) as mo:
        with patch('memeoverflow.memeoverflow.random') as random:
            # text should be on line 2 for this template
            random.choice.return_value = 'PETER_PARKER_CRY'
            meme, text0, text1 = mo.choose_meme_template('test')
            assert meme == 'PETER_PARKER_CRY'
            assert text0 is None
            assert text1 == 'test'

            # first attempt rejected due to ending in question mark
            # second attempt ok because template requires ending question mark
            random.choice.return_value = None
            random.choice.side_effect = [
                'BUT_THATS_NONE_OF_MY_BUSINESS',
                'PHILOSORAPTOR',
            ]
            meme, text0, text1 = mo.choose_meme_template('test?')
            assert meme == 'PHILOSORAPTOR'
            assert text0 == 'test?'
            assert text1 is None

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
                'BATMAN_SLAPPING_ROBIN',
            ]
            meme, text0, text1 = mo.choose_meme_template('test')
            assert meme == 'BATMAN_SLAPPING_ROBIN'
            assert text0 == 'test'
            assert text1 is None

def test_mo_make_meme():
    data = {
        'username': 'imgflip_user',
        'password': 'imgflip_pass',
        'template_id': BATMAN_SLAPPING_ROBIN,
        'text0': 'test',
        'text1': None,
    }

    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key, test_db) as mo:
        with patch('memeoverflow.memeoverflow.requests') as requests:
            with patch('memeoverflow.memeoverflow.random') as random:
                random.choice.return_value = 'BATMAN_SLAPPING_ROBIN'
                mock_response = Mock(json=Mock(return_value=example_imgflip_response))
                requests.post.return_value = mock_response
                img_url, meme_name = mo.make_meme('test')
                requests.post.assert_called_once_with(imgflip_url, data=data)
                assert img_url == example_imgflip_img_url
                assert meme_name == 'BATMAN_SLAPPING_ROBIN'

def test_mo_make_meme_fail_retry():
    data = {
        'username': 'imgflip_user',
        'password': 'imgflip_pass',
        'template_id': BATMAN_SLAPPING_ROBIN,
        'text0': 'test',
        'text1': None,
    }

    with MemeOverflow(fake_twitter, fake_imgflip, fake_stack_no_key, test_db) as mo:
        with patch('memeoverflow.memeoverflow.requests') as requests:
            with patch('memeoverflow.memeoverflow.random') as random:
                with patch('memeoverflow.memeoverflow.sleep') as sleep:
                    with patch('memeoverflow.memeoverflow.logger') as logger:
                        random.choice.return_value = 'BATMAN_SLAPPING_ROBIN'
                        mock_response = Mock(json=Mock(return_value=example_imgflip_response))

                        requests.post.side_effect = ConnectionError()
                        mo.make_meme('test')
                        requests.post.assert_called_once_with(imgflip_url, data=data)
                        logger.error.assert_called_once()

                        requests.post.side_effect = None
                        requests.post.return_value = mock_response
                        img_url, meme_name = mo.make_meme('test')
                        assert img_url == example_imgflip_img_url
                        assert meme_name == 'BATMAN_SLAPPING_ROBIN'

def test_mo_tweet():
    pass
