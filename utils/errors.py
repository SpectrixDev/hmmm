class HmmException(Exception):
    pass

class SubredditNotFound(HmmException):
    def __init__(self, subreddit: str, status_code: int = 404):
        self.subreddit = subreddit
        super().__init__(f"Could not get r/{subreddit}, HTTP status code {status_code}")

class UnhandledStatusCode(HmmException):
    def __init__(self, status_code: int, url: str, reason: str):
        self.status_code = status_code
        self.url = url
        self.reason = reason
        super().__init__(f"Requesting {url} returned {status_code} {reason}")
        