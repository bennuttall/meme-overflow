from memeoverflow import MemeOverflow
from logzero import logfile

logfile('/var/log/memeoverflow/example.log')  # optional

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

db_path = '/home/ben/bots/memes/memes.db'

main = MemeOverflow(
    twitter=twitter,
    imgflip=imgflip,
    stackexchange=stackexchange,
    db_path=db_path
)

if __name__ == '__main__':
    while True:
        main()
