import asyncio
import datetime
import discord
import logging
import random
from discord.ext import commands
from collections import Counter, deque
from hmmm.cogs.handler import DM_MESSAGE, GUILD_MESSAGE
from hmmm.objects import Post, SubredditNotFound, UnhandledStatusCode

log = logging.getLogger(__name__)
accepted_extensions = [
    ".png", 
    ".jpg", 
    ".jpeg",
    ".gif", 
    ".gifv", 
    ".webm",
    ".mp4", 
    ".mp3"
]


class SubredditHandler:
    def __init__(self, bot, maxlen: int = 500):
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
            "used": Counter(),
            "unused": Counter()
        }

        for k, v in self.history.items():
            data["used"][k] = len(v)

        for k, v in self.cache.items():
            data["unused"][k] = len(v)

        return data

    async def get_post(self, subreddit):
        
        if not self.cache.get(subreddit):
            self.cache[subreddit] = list()
        
        if not self.history.get(subreddit):
            self.history[subreddit] = deque(maxlen=self.maxlen)

        if self.cache.get(subreddit, []) == []:
            attempts = 0
            while attempts < 5:
                async with self.bot.session.get(f"https://reddit.com/r/{subreddit}/new.json?sort=top&limit=500") as resp:
                    if not resp.content_type == "application/json":
                        data = await resp.content.read()
                        message = (
                            "",
                            "`HTTP {0.status} {0.reason}`".format(resp),
                            "`Content Type:` `%s`" % resp.content_type,
                            "Content: ", await resp.content.read()
                        )
                        await self.bot.get_cog("EventHandler").webhook_log("\n".join(message))

                    data = await resp.json()
                    log.debug("{0.method} {0._url} {0.status} {0.reason}".format(resp))

                    if resp.status == 200:
                        if len(data["data"]["children"]) == 0:
                            raise SubredditNotFound(subreddit, resp.status)

                        log.debug(f"r/{subreddit}: generating objects")

                        for obj in data["data"]["children"]:

                            url = obj["data"].get("url")

                            if not url or not any(url.endswith(x) for x in accepted_extensions):
                                continue
                            if any(c.url == url for c in self.history.get(subreddit, [])):
                                continue
                            
                            kls = Post(
                                title=obj["data"]["title"],
                                url=url,
                                is_nsfw=obj["data"]["over_18"]
                            )

                            self.cache[subreddit].append(kls)
                            log.debug(f"r/{subreddit}: {kls}")

                        log.debug(f"r/{subreddit}: refreshed cache")
                        if len(self.cache[subreddit]) == 0:
                            log.debug("Nothing added, returning a item from the history")
                            return random.choice(self.history.get(subreddit))
                        else:
                            log.debug("everything went as intended!")
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

        if ctx.guild and sub.nsfw and not ctx.channel.is_nsfw():
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
            title="ImageFetcher statistics",
            color=discord.Color.dark_purple(),
            description=str()
        )
        for type in result:
            embed.description += f"\n**{type.title()}**:\n"
            for sub, count in result[type].items():
                embed.description += f"__r/{sub}__: {count}\n"
            
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ImageFetcher(bot))
