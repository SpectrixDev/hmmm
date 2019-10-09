# Miscellanous objects that helps with the bot
import logging



class ANSIFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt="[{asctime} {name}/{levelname}]: {message}", datefmt=r"%Y/%m/%d %H:%M:%S", style="{")
        self.codes = {
            "WARN": "\33[33m",
            "CRITICAL": "\33[95m",
            "ERROR": "\33[31m",
            "DEBUG": "\33[32;1m",
            "RESET": "\33[0m"
        }

    def format(self, r):
        if r.levelname == "WARNING":
            r.levelname = "WARN"
        if r.levelname in self.codes:
            r.msg = self.codes[r.levelname] + str(r.msg) + self.codes["RESET"]
        
        return super().format(r)