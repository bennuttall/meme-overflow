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

main = MemeOverflow(twitter, imgflip, stackexchange)

if __name__ == '__main__':
    main()
