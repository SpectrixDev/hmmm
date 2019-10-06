import logging
import asyncio
import random

log = logging.getLogger(__name__)
accepted_extensions = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]


class HmmException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class SubredditNotFound(HmmException):
    def __init__(self, subreddit, status_code: int=404):
        self.subreddit = subreddit
        message = "Cannot find r/{0}, received {1} status code"
        super().__init__(message.format(subreddit, status_code))

class UnhandledStatusCode(HmmException):
    def __init__(self, status_code: int, url: str, reason: str):
        self.status_code = status_code
        self.url = url
        self.reason = reason

        message = "Unhandled status code {0}, reason: {1}"
        super().__init__(message.format(status_code, reason))

class Post:
    def __init__(self, title: str, url: str, is_nsfw: bool=False):
        self.title = title
        self.url = url
        self.nsfw = is_nsfw
    

    def __repr__(self):
        return "<Post title={0.title} is_nsfw={0.nsfw} url={0.url}>".format(self)
    
    def __str__(self):
        return self.url
    
    def __bool__(self):
        return self.nsfw
    


class SubredditHandler:
    def __init__(self, bot, maxlen: int=400):
        self.history = {
            # subreddit: deque()
        }
        self.cache = {
            # subreddit : a cache of json objects from each HTTP Request.
        }
        # a JSON object from a HTTP request, it will be changed frequently.
        self.maxlen = maxlen
        self.bot = bot
    

    async def get_post(self, subreddit):
        if self.cache.get(subreddit, {}) == {}:
            attempts = 0
            while attempts < 5:
                async with self.bot.session.get(f"https://reddit.com/r/{subreddit}/hot.json?limit=200") as resp:
                    log.info("{0.method} {0._url} {0.status} {0.reason}".format(resp))
                    
                    try:
                        data = await resp.json()
                    except (ValueError, TypeError):
                        data = {}

                    if resp.status == 200:
                        log.info(f"r/{subreddit}: generating objects")

                        if not self.cache.get(subreddit):
                            self.cache[subreddit] = set()

                        for obj in data["data"]["children"]:

                            url = obj["data"].get("url")
                            if url and any(url.endswith(x) for x in accepted_extensions) and not any(c.url == url for c in self.history.get(subreddit, set())):
                                kls = Post(
                                    title=obj["data"]["title"],
                                    url=url,
                                    is_nsfw=obj["data"]["over_18"]
                                )
                                if kls.title == "hmmm":
                                    kls.title = ""

                                self.cache[subreddit].add(kls)
                                log.info(f"r/{subreddit}: {kls}")

                        log.info(f"r/{subreddit}: refreshed cache")
                        break
                    
                    elif resp.status == 404:
                        raise SubredditNotFound(subreddit, 404)

                    elif resp.status == 329:
                        log.warning(f"Reddit is ratelimiting us, reason: {resp.reason}, json?: {data}")
                        if not self.history.get(subreddit):
                            await asyncio.sleep(5)
                        else:
                            return random.choice(self.history[subreddit])
                    
                    else:
                        raise UnhandledStatusCode(resp.status_code, resp._url, resp.reason)
        


        val = self.cache[subreddit].pop()
        if not subreddit in self.history:
            self.history.update({ subreddit : set([val]) })
        else:
            
            self.history[subreddit].add(val)

        return val


        
        