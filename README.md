# Meme Overflow

[![](https://badge.fury.io/py/memeoverflow.svg)](https://badge.fury.io/py/memeoverflow)
[![](https://api.travis-ci.org/bennuttall/meme-overflow.svg?branch=master)](https://travis-ci.org/bennuttall/meme-overflow)
[![](https://img.shields.io/codecov/c/github/bennuttall/meme-overflow/master.svg?maxAge=2592000)](https://codecov.io/github/bennuttall/meme-overflow)

A simple framework for Twitter bots creating memes from Stack Exchange
questions.

Take questions posted on a particular Stack Exchange site, generate a meme out
of them and tweet them.

![](fry.jpg)

Uses the following APIs:

- [Stack Exchange](https://api.stackexchange.com/)
- [Twitter](https://developer.twitter.com/en/docs/api-reference-index) (via
[Twython](https://twython.readthedocs.io/en/latest/))
- [imgflip](https://api.imgflip.com/)

## Instances

- [@pi_stack](https://twitter.com/pi_stack) (Raspberry Pi)
- [@overflow_meme](https://twitter.com/overflow_meme) (Stack Overflow)
- [@worldbuildingme](https://twitter.com/worldbuildingme) (World Building)
- [@askubuntumemes](https://twitter.com/askubuntumemes) (Ask Ubuntu)
- [@stackamemia](https://twitter.com/stackamemia) (Academia)

## Run your own instance

You can run your own instance of a Twitter bot following a particular Stack
Exchange site. You need to register for API keys for the relevant services.

### API keys

1. Sign up for a [Twitter](https://twitter.com/) account, [create an
app](https://developer.twitter.com/en/apps) and get your four API keys.

1. Sign up for an [imgflip](https://imgflip.com/) account and note your username
and password.

1. Register for a [Stack Exchange App Key](https://stackapps.com/apps/oauth/register)
and find your user ID for each site (click on your avatar to go to your user
page and your ID is the number in the URL e.g. `806889` in
[stackoverflow.com/users/806889/ben-nuttall](https://stackoverflow.com/users/806889/ben-nuttall)) -
note these are different for each site.

### Essential setup

1. Install this project:

    ```bash
    sudo pip3 install memeoverflow
    ```

1. Copy the example script `example.py` (e.g. to `raspberrypi.py`) and edit your
copy to specify:

    - the Stack Exchange site you wish to follow (get the exact string
    [here](https://api.stackexchange.com/docs/questions)) and your Stack
    Exchange API key
    - your Twitter account's API keys
    - your imgflip's username and password
    - the path to your meme database file (can be a non-existent file, as long as
    the file location can be written to)
    - Optionally, the path to your log file (can be a non-existent file, as long
    as the file location can be written to)

### log file (optional)

If you want to log to a file, populate the `logfile` function call as provided
in the `example.py` script.

If the path to the provided log file is writeable by your user, you are ready to
go. Here's an example of what you need to write logs to
`/var/log/memeoverflow/`:

1. Create the directory and chown it:

    ```bash
    sudo mkdir /var/log/memeoverflow
    sudo chown ben: /var/log/memeoverflow
    ```

1. Set the logfile to e.g. `/var/log/memeoverflow/raspberrypi.log` in
`raspberrypi.py`

### Simple launch (option 1)

1. Run it directly:

```bash
python3 raspberrypi.py
```

Log entries will be written to stdout (and optionally to a log file if
specified). You'll have to keep the process active to keep it running, unless
you background it with `&`. Alternatively, use systemd.

### systemd launch (option 2)

Alternatively, use systemd:

1. Copy the example systemd service `memeoverflow-example.service` into `/etc/systemd/system/`:

    ```bash
    sudo cp memeoverflow example.service /etc/systemd/system/memeoverflow-raspberrypi.service
    ```

1. Edit the service (edit `Description` and path to file in `ExecStart`):

    ```bash
    sudo vim /etc/systemd/system/memeoverflow-raspberrypi.service
    ```

1. Reload systemctl daemon:

    ```bash
    sudo systemctl daemon-reload
    ```

1. Enable and start the service:

    ```bash
    sudo systemctl enable memeoverflow-raspberrypi.service
    sudo systemctl start memeoverflow-raspberrypi.service
    ```

1. Check the status:

    ```bash
    sudo systemctl status memeoverflow-raspberrypi.service
    ```

If a log file is specified, log entries will be written there. They will also be
visible in `systemctl status` which gives real evidence of it running correctly.
