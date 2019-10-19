
class HmmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SubredditNotFound(HmmException):
    def __init__(self, subreddit, status_code: int = 404):
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
