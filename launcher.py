#!venv/bin/python
try:
    import ujson as json
except ImportError:
    import json

import logging
import ctypes
import sys
import asyncio
from hmmm import Hmmm
from datetime import datetime
from hmmm.utils import ANSIFormatter


log = logging.getLogger("hmmm")
log.setLevel(logging.DEBUG)


FILENAME = datetime.utcnow().strftime("logs/%Y-%m-%d_%H-%M-%S.log")



if sys.platform != "win32":
    try:
        import uvloop
    except ImportError:
        log.error("Importing uvloop failed, ignoring")
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

else:
    # workaround for ANSI rendering for the command prompt and other consoles 
    k32 = ctypes.windll.kernel32
    k32.SetConsoleMode(k32.GetStdHandle(-11), 7)




def launch():
    
    logfile = logging.FileHandler(FILENAME, "w", "utf-8")
    handler = logging.StreamHandler()
    handler.setFormatter(ANSIFormatter())

    log.addHandler(logfile)
    log.addHandler(handler)

    with open("config.json") as f:
        config = json.load(f)
    

    bot = Hmmm(config=config)
    bot.run(config["bot_token"])


launch()
    
    

