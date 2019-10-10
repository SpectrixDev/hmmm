#!venv/bin/python
try:
    import ujson as json
except ImportError:
    import json

import logging
import ctypes
import sys
import os
import asyncio
from hmmm import Hmmm
from datetime import datetime


log = logging.getLogger("hmmm")
log.setLevel(logging.DEBUG)
FILENAME = datetime.utcnow().strftime("logs/%Y-%m-%d_%H-%M-%S.log")


if sys.platform != "win32":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        log.error("Importing uvloop failed, ignoring")

else:
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
    # workaround for ANSI rendering for the command prompt and other consoles 
    k32 = ctypes.windll.kernel32
    k32.SetConsoleMode(k32.GetStdHandle(-11), 7)


class LogFormatter(logging.Formatter):
    def __init__(self, use_ansi=True):
        if use_ansi:
            super().__init__(fmt="\033[1;30m[{asctime} {name}/{levelname}]: {message}", datefmt=r"%Y/%m/%d %H:%M:%S", style="{")
        else:
            super().__init__(fmt="[{asctime} {name}/{levelname}]: {message}", datefmt=r"%Y/%m/%d %H:%M:%S", style="{")
        self.use_ansi = use_ansi
        self.codes = {
            "WARN": "\033[33m",
            "CRITICAL": "\033[95m",
            "ERROR": "\033[31m",
            "DEBUG": "\033[32;1m",
            "RESET": "\033[0m",
            "INFO" : "\033[1;32m"
        }

    def format(self, r: logging.LogRecord):
        if r.levelname == "WARNING":
            r.levelname = "WARN"
        if r.levelname in self.codes and self.use_ansi:
            r.msg = self.codes[r.levelname] + str(r.msg) + self.codes["RESET"]
        return super().format(r)







def launch():    
    if not os.path.exists("logs"):
        os.mkdir("logs")

    


    logfile = logging.FileHandler(FILENAME, "w", "utf-8")
    handler = logging.StreamHandler()

    handler.setFormatter(LogFormatter())
    logfile.setFormatter(LogFormatter(use_ansi=False))
    
    log.handlers = [logfile, handler]
    
    with open("config.json") as f:
        config = json.load(f)
        bot = Hmmm(config=config)
        bot.run(config["bot_token"])


launch()