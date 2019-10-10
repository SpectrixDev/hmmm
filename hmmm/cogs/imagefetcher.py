import asyncio
import datetime
import discord
import logging
import random
from collections import Counter, deque
from discord.ext import commands


log = logging.getLogger(__name__)
accepted_extensions = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4",".mp3"]


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
    def __init__(self, bot, maxlen: int=500):
        self.history = {
            # subreddit: []
        }
        self.cache = {
            # subreddit : a cache of json objects from each HTTP Request.
        }
        # a JSON object from a HTTP request, it will be changed frequently.
        self.maxlen = maxlen
        self.bot = bot
    

        

    def debug_stats(self):
        data = {
            "history" : Counter(),
            "http_cache" : Counter()
        }

        for k, v in self.history.items():
            data["history"][k] = len(v)
        
        
        for k, v in self.cache.items():
            data["http_cache"][k] = len(v)
    
        return data   


    async def get_post(self, subreddit):
        if self.cache.get(subreddit, []) == []:
            attempts = 0
            while attempts < 5:
                async with self.bot.session.get(f"https://reddit.com/r/{subreddit}/new.json?sort=top&limit=500") as resp:
                    log.debug("{0.method} {0._url} {0.status} {0.reason}".format(resp))
                    
                    try:
                        data = await resp.json()
                    except (ValueError, TypeError):
                        data = {}

                    if resp.status == 200:
                        if len(data["data"]["children"]) == 0:
                            raise SubredditNotFound(subreddit, resp.status)

                        log.debug(f"r/{subreddit}: generating objects")

                        if not self.cache.get(subreddit):
                            self.cache[subreddit] = list()

                        for obj in data["data"]["children"]:

                            url = obj["data"].get("url")
                            if url and any(url.endswith(x) for x in accepted_extensions) and not any(c.url == url for c in self.history.get(subreddit, [])):
                                kls = Post(
                                    title=obj["data"]["title"],
                                    url=url,
                                    is_nsfw=obj["data"]["over_18"]
                                )
                                if kls.title == "hmmm":
                                    kls.title = ""

                                self.cache[subreddit].append(kls)
                                log.debug(f"r/{subreddit}: {kls}")
                            

                        log.debug(f"r/{subreddit}: refreshed cache")
                        if len(self.cache[subreddit]) == 0:
                            log.debug("exec")
                            return random.choice(self.history.get(subreddit))
                        else:
                            log.debug("exec1")
                            break
                    

                    elif resp.status == 329:
                        log.warning(f"Reddit is ratelimiting us, reason: {resp.reason}, json?: {data}")
                        if not self.history.get(subreddit):
                            await asyncio.sleep(5)
                        else:
                            return random.choice(self.history[subreddit])
                    
                    else:
                        raise UnhandledStatusCode(resp.status_code, resp._url, resp.reason)
        

        val = self.cache[subreddit].pop()
        log.debug(f"fetched {val} from cache")
        if not subreddit in self.history:
            self.history.update({ subreddit : deque(maxlen=self.maxlen, iterable=[val]) })
        else:
            self.history[subreddit].append(val)

        return val



class ImageFetcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.handler = SubredditHandler(self.bot)
    


    async def send_sub(self, ctx, subreddit):
        try:
            sub = await self.handler.get_post(subreddit)
        except UnhandledStatusCode as error:
            log.error(error)
            return await ctx.send(error)

        if sub.nsfw and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            if len(sub.title) == 0:
                await ctx.send(sub.url)
            else:
                await ctx.send(f"**{sub.title[:100]}**\n{sub.url}")
    

    @commands.command(aliases=['hm', 'hmm', 'hmmmm', 'hmmmmm'])
    async def hmmm(self, ctx):
        async with ctx.channel.typing():
            await self.send_sub(ctx, "hmmm")
    
    @commands.command(aliases=['cursedimage', 'cursedimages'])
    async def cursed(self, ctx):
        await self.send_sub(ctx, "cursedimages")

    @commands.command()
    async def ooer(self, ctx):
        await self.send_sub(ctx, "Ooer")

    @commands.command(aliases=['surreal', 'surrealmemes'])
    async def surrealmeme(self, ctx):
        await self.send_sub(ctx, "surrealmemes")

    @commands.command(aliases=['imsorryjon', 'imsorryjohn'])
    async def imsorry(self, ctx):
        await self.send_sub(ctx, "imsorryjon")
    
    
    @commands.command(name="healthcheck", aliases=["dbgstats", "hc"])
    async def debug_stats(self, ctx):
        result = self.handler.debug_stats()
        embed = discord.Embed(
            title="\U0001f493 Cache stats",
            color=discord.Color.dark_purple(),
            description=str()
        )

        embed.description += f"History cache: {len(result['history'])}\n"
        for sub, count in result["history"].items():
            embed.description += f"__**r/{sub}**__: {count}\n"
        
        
        embed.description += f"\nUnused cache: {len(result['http_cache'])}\n"
        for sub, count in result["http_cache"].items():
            embed.description += f"__**r/{sub}**__: {count}\n"
        
        await ctx.send(embed=embed)

  

def setup(bot):
    bot.add_cog(ImageFetcher(bot))
