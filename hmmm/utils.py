# Miscellanous objects that helps with the bot
import logging



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