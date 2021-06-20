from io import BytesIO
import shutil

import requests


def tags_to_hashtags(tags):
    """
    Replace special characters from list of tags, de-dupe and return string of
    hashtags.

    e.g. tags_to_hashtags(['foo', 'bar', 'foobar', 'foo-bar'])
         => '#foo #bar #foobar'
    """
    hashtags = set()
    replacements = (
        ('.net', 'dotnet'),
        ('c#', 'csharp'),
        ('f#', 'fsharp'),
        ('c++', 'cpp'),
        ('g++', 'gpp'),
        ('python2x', 'python2'),
        ('python3x', 'python3'),
        ('-', ''),
        ('.', ''),
        ('b+', 'bplus'),
    )
    for tag in tags:
        for a, b in replacements:
            tag = tag.replace(a, b)
        try:
            int(tag)
        except ValueError:
            hashtags.add(f'#{tag}')
    return ' '.join(hashtags)

def download_image_bytes(img_url):
    "Download an image and return its contents"
    r = requests.get(img_url)
    r.raise_for_status()
    return BytesIO(r.content)

def download_image_file(img_url, path):
    "Download an image file and save it"
    r = requests.get(img_url, stream=True)
    with open(path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
