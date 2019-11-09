from logging import Formatter, LogRecord


class Post:
    def __init__(self,
                 up: int,
                 down: int,
                 url: str,
                 title: str,
                 subreddit: str,
                 nsfw: bool = False
        ):
        self.title = title
        self.url = url
        self.subreddit = subreddit
        self.nsfw = nsfw
        self.guild_ids = set()
        self.up = up
        self.down = down

    def __repr__(self):
        return "<Post subreddit='{0.subreddit}' title='{0.title}' up={0.up} down={0.down} nsfw={0.nsfw} url='{0.url}'>".format(self)

    def __str__(self):
        return self.url

    def __bool__(self):
        return self.nsfw


class LogFormatter(Formatter):
    def __init__(self, use_ansi: bool = True):
        self.use_ansi = use_ansi
        self.codes = {
            "WARN": "\033[33m",
            "CRITICAL": "\033[95m",
            "ERROR": "\033[31m",
            "DBUG": "\033[34;1m",
            "RESET": "\033[0m",
            "INFO": "\033[1;32m",
            "START" : "\033[1;30m"
        }

        if use_ansi:
            super().__init__(
                fmt=self.codes["START"] + '[{asctime} {name}/{levelname}]:' + self.codes["RESET"] + ' {message}',
                datefmt=r"%Y/%m/%d %H:%M:%S",
                style="{"
            )
        else:
            super().__init__(
                fmt="[{asctime} {name}/{levelname}]: {message}",
                datefmt=r"%Y/%m/%d %H:%M:%S",
                style="{"
            )

        

    def format(self, r: LogRecord):
        rename_lvls = {
            "WARNING" : "WARN",
            "DEBUG" : "DBUG"
        }
        new_name = rename_lvls.get(r.levelname)
        if new_name is not None:
            r.levelname = new_name

        if r.levelname in self.codes and self.use_ansi:
            r.msg = self.codes[r.levelname] + str(r.msg) + self.codes["RESET"]
        return super().format(r)
