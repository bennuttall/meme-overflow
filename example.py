from memegenerator import MemeGenerator

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

mg = MemeGenerator(twitter, imgflip, stackexchange)
mg.main()
