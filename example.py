from memeoverflow import MemeOverflow

stackexchange = {
    'site': '',
    'key': '',
}

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

mo = MemeOverflow(twitter, imgflip, stackexchange)
mo.main()
