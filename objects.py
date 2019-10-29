from logging import Formatter, LogRecord
from discord.ext.commands import Context, BotMissingPermissions, Command, Group



# in design

class HelpCommand:
    def __init__(self,
        context: Context,
        verify_checks: bool=True,
        line_height_span: int=20
    ):
        self.author = context.author
        self.lhs = line_height_span
        self.emojis = {
            "GROUP" : "\U0001f4c2",
            "COMMAND" : "\U0001f449",
            "DISABLED" : "\U0001f512"
        }
        self.verify_checks = verify_checks
        self.bot = context.bot

    def generate_command_line(self, command):
        if not isinstance(command, (Command, Group)):
            raise TypeError("Expected Command or Group, got {0.__class__.__name__}".format(command))
        # /shrug




class HmmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SubredditNotFound(HmmException):
    def __init__(self, subreddit: str, status_code: int = 404):
        self.subreddit = subreddit
        message = "Cannot find r/{0}, received {1} status code"
        super().__init__(message.format(subreddit, status_code))

class UnhandledStatusCode(HmmException):
    def __init__(self, status_code: int, url: str, reason: str):
        self.status_code = status_code
        self.url = url
        self.reason = reason
        super().__init__("%d %s" % (status_code, reason))

class Post:
    def __init__(self, title: str, url: str, is_nsfw: bool = False):
        self.title = title
        self.url = url
        self.nsfw = is_nsfw

    def __repr__(self):
        return "<Post title={0.title} is_nsfw={0.nsfw} url={0.url}>".format(self)

    def __str__(self):
        return self.url

    def __bool__(self):
        return self.nsfw

class LogFormatter(Formatter):
    def __init__(self, use_ansi: bool=True):
        if use_ansi:
            super().__init__(
                fmt="\033[1;30m[{asctime} {name}/{levelname}]: {message}",
                datefmt=r"%Y/%m/%d %H:%M:%S",
                style="{"
            )
        else:
            super().__init__(
                fmt="[{asctime} {name}/{levelname}]: {message}",
                datefmt=r"%Y/%m/%d %H:%M:%S",
                style="{"
            )

        self.use_ansi = use_ansi
        self.codes = {
            "WARN": "\033[33m",
            "CRITICAL": "\033[95m",
            "ERROR": "\033[31m",
            "DEBUG": "\033[32;1m",
            "RESET": "\033[0m",
            "INFO" : "\033[1;32m"
        }

    def format(self, r: LogRecord):
        if r.levelname == "WARNING":
            r.levelname = "WARN"
        if r.levelname in self.codes and self.use_ansi:
            r.msg = self.codes[r.levelname] + str(r.msg) + self.codes["RESET"]
        return super().format(r)





class CustomContext(Context):

    async def send(self, *args, **kwargs):
        if not self.guild.me.permissions_in(self.channel).send_messages:
            raise BotMissingPermissions(["send_messages"])

        return await super().send(*args, **kwargs)