import pytest


@pytest.fixture()
def test_db():
    return 'test_memes.db'

@pytest.fixture()
def fake_twitter():
    return {
        'con_key': 'tw_con_key',
        'con_sec': 'tw_con_sec',
        'acc_tok': 'tw_acc_tok',
        'acc_sec': 'tw_acc_sec',
    }

@pytest.fixture()
def fake_imgflip():
    return {
        'username': 'imgflip_user',
        'password': 'imgflip_pass',
    }

@pytest.fixture()
def fake_stack_no_key():
    return {
        'site': 'stackexchange',
    }

@pytest.fixture()
def fake_stack_with_key():
    return {
        'site': 'stackexchange',
        'key': 'stack_key',
    }

@pytest.fixture()
def fake_stack_with_key_and_userid():
    return {
        'site': 'stackexchange',
        'key': 'stack_key',
        'user_id': 12345,
    }

@pytest.fixture()
def example_se_item_1():
    return {
        'tags': ['tag', 'another-tag'],
        'question_id': 123456,
        'link': 'https://stackexchange.stackexchange.com/questions/123456/some-question',
        'title': 'Some question'
    }

@pytest.fixture()
def example_se_item_2():
    return {
        'tags': ['tag', 'another-tag'],
        'question_id': 123457,
        'link': 'https://stackexchange.stackexchange.com/questions/123457/anther-question',
        'title': 'Another question'
    }

@pytest.fixture()
def example_se_response(example_se_item_1, example_se_item_2):
    return {
        'items': [example_se_item_1, example_se_item_2],
        'has_more': True,
        'quota_max': 300,
        'quota_remaining': 299,
    }

@pytest.fixture()
def empty_dict():
    return {}

@pytest.fixture()
def example_imgflip_img_url():
    return 'https://i.imgflip.com/test.jpg'

@pytest.fixture()
def example_imgflip_response(example_imgflip_img_url):
    return {
        'success': True,
        'data': {
            'url': example_imgflip_img_url,
            'page_url': 'https://imgflip.com/i/test'
        }
    }

@pytest.fixture()
def example_twitter_upload_response():
    return {
        'media_id': '1234567890',
    }

@pytest.fixture()
def example_question():
    return {
        'title': 'question_title',
        'link': 'question_url',
        'question_id': 12345,
        'tags': ['foo', 'bar', 'foobar'],
    }

@pytest.fixture()
def example_long_question():
    return {
        'title': 'very_very_long_question_title_really_long',
        'link': 'very_very_long_question_url_really_long',
        'question_id': 12345,
        'tags': [
            'aaaaaaaaa1', 'aaaaaaaaa2', 'aaaaaaaaa3', 'aaaaaaaaa4',
            'aaaaaaaaa5', 'aaaaaaaaa6', 'aaaaaaaaa7', 'aaaaaaaaa8',
            'aaaaaaaaa9', 'aaaaaaaa10', 'aaaaaaaa11', 'aaaaaaaa12',
            'aaaaaaaa13', 'aaaaaaaa14', 'aaaaaaaa15', 'aaaaaaaa16',
            'aaaaaaaa17', 'aaaaaaaa18', 'aaaaaaaa19', 'aaaaaaaa20',
        ]
    }

@pytest.fixture()
def stack_url():
    return 'https://api.stackexchange.com/2.2/questions'

@pytest.fixture()
def imgflip_url():
    return 'https://api.imgflip.com/caption_image'

@pytest.fixture()
def BATMAN_SLAPPING_ROBIN():
    return 438680

@pytest.fixture()
def example_imgflip_img_blob():
    return b"blob"
