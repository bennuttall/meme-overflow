# Meme Overflow

Take questions posted on a particular Stack Exchange site, generate a meme out
of it and tweet it.

![](fry.jpg)

## Instances

- [@pi_stack](https://twitter.com/pi_stack) (Raspberry Pi)
- [@overflow_meme](https://twitter.com/overflow_meme) (Stack Overflow)
- [@worldbuildingme](https://twitter.com/worldbuildingme) (World Building)
- [@askubuntumemes](https://twitter.com/askubuntumemes) (Ask Ubuntu)

## Run your own instance

1. Sign up for a [Twitter](https://twitter.com/) account, [create an
app](https://developer.twitter.com/en/apps) and get your four API keys.

1. Sign up for an [imgflip](https://imgflip.com/) account and note your username
and password.

1. Register for a [Stack Exchange App Key](https://stackapps.com/apps/oauth/register)

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

1. Run it:

```bash
python3 raspberrypi.py
```
