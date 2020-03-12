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
fake_stack_with_key = {
    'site': 'stackexchange',
    'key': 'stack_key',
}
fake_stack_with_key_and_userid = {
    'site': 'stackexchange',
    'key': 'stack_key',
    'user_id': 12345,
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
empty_dict = {}

example_imgflip_img_url = 'https://i.imgflip.com/test.jpg'

example_imgflip_response = {
    'success': True,
    'data': {
        'url': example_imgflip_img_url,
        'page_url': 'https://imgflip.com/i/test'
    }
}

example_twitter_upload_response = {
    'media_id': '1234567890',
}

example_question = {
    'title': 'question_title',
    'link': 'question_url',
    'question_id': 12345,
    'tags': ['foo', 'bar', 'foobar'],
}

stack_url = 'https://api.stackexchange.com/2.2/questions'
imgflip_url = 'https://api.imgflip.com/caption_image'

BATMAN_SLAPPING_ROBIN = 438680

example_imgflip_img_blob = b"blob"
