# Miscellanous objects that helps with the bot
import logging



class ANSIFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt="\033[1;30m[{asctime} {name}/{levelname}]: {message}", datefmt=r"%Y/%m/%d %H:%M:%S", style="{")
        self.codes = {
            "WARN": "\033[33m",
            "CRITICAL": "\033[95m",
            "ERROR": "\033[31m",
            "DEBUG": "\033[32;1m",
            "RESET": "\033[0m",
            "INFO" : "\033[1;32m"
        }

    def format(self, r):
        if r.levelname == "WARNING":
            r.levelname = "WARN"
        if r.levelname in self.codes:
            r.msg = self.codes[r.levelname] + str(r.msg) + self.codes["RESET"]
        
        return super().format(r)