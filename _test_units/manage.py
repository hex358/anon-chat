import sys
import asyncio
import json

import keyboard
import main
from threading import Thread
import subprocess
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def set_interrupted(key):
    with open("base/general.json", "r+") as base:
        interrupt_text = json.loads(base.read())
        interrupt_text["_interrupted"] = key
        base.seek(0)
        base.write(json.dumps(interrupt_text))
        base.truncate()

def interrupt_handler():
    while 1:
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("0"):
            set_interrupted(True)
            return 0


async def launch():
    Thread(target=interrupt_handler).start()
    await main.main()

async def test():
    main.a = 2
    print(main.a)
    pass

async def exit():
    await main.exit()

async def send():
    text = json.load(open('base/newsletter.json', 'r'))["text"]
    await main.newsletter_handler(text)

if __name__ == '__main__':
    set_interrupted(False)
    asyncio.run(globals()[sys.argv[1]]())