from memeoverflow import MemeDatabase
import sys

db = MemeDatabase('raspberrypi')

if len(sys.argv) > 1:
    arg = sys.argv[1]
    try:
        meme_id = int(arg)
        meme_name = db.select_meme(meme_id)
        db.blacklist_meme(meme_id)
        print(f'Blacklisted: {meme_name}')
    except ValueError:
        results = db.search_for_meme(arg)
        for id, name, blacklisted in results:
            print(f"{id}: {name} {'(blacklisted)' if blacklisted else ''}")
else:
    print('No argument provided')
