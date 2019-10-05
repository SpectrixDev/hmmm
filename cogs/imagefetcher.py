import asyncio
import datetime
import discord
import logging
import random
from collections import deque
from discord.ext import commands

acceptableImageFormats = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]
memeHistory = deque()

log = logging.getLogger(__name__)



class SubredditHandler:
    def __init__(self, bot, maxlen: int=400):
        self._items = {
            # r/subreddit: deque()
        }
        self.maxlen = maxlen
        self.bot = bot
    

    async def get_post(self, sub):
        if not sub in self._items:
            self._items.update({ sub : deque(maxlen=self.maxlen) })

        attempts = 0
                    
        while attempts < 5:
            async with self.bot.session.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=100") as resp:
                data = await resp.json()
                log.debug("{0.method} {0._url} {0.status}".format(resp))
                if resp.status == 200:

                    result = {
                        "nsfw" : True,
                        "title" : None,
                        "url" : None
                    }
                    for object in data['data']['children']:
                        if 'url' in object['data'] and not any(x["url"] == object["data"]["url"] for x in self._items.get(sub, [])):
                            if not any(object["data"]["url"].lower().endswith(x) for x in acceptableImageFormats):
                                continue

                            result["url"] = str(object['data']['url']) 
                            result["nsfw"] = object['data']['over_18']

                            log.debug( str(object['data']['title']))

                            if str(object['data']['title']) == "hmmm":
                                result["title"] = ""
                            else:
                                result["title"] = f"**{str(object['data']['title'])}**"
                            self._items[sub].append(result)

                            log.debug(result)
                            return result


                elif resp.status == 429:
                    log.warning("Reddit has returned a 429'er")
                    log.warning(data)
                    # if we already have some urls in the cache then we should use it!
                    if self._items.get(sub) and len(self._items[sub]) > 0:
                        return random.choice(self._items.get(sub))
                    
                    await asyncio.sleep(8)
                
                attempts += 1
        return {"nsfw" : False, "title" : "Error", "url" : "could not fetch url"}
        


class ImageFetcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['hm', 'hmm', 'hmmmm', 'hmmmmm'])
    async def hmmm(self, ctx):
        async with ctx.channel.typing():
            sub = await self.bot.handler.get_post("hmmm")
            if sub["nsfw"] and not ctx.channel.is_nsfw():
                raise commands.NSFWChannelRequired(ctx.channel)
            else:
                await ctx.send(f"{sub['title']}\n{sub['url']}")
    
    @commands.command(aliases=['cursedimage', 'cursedimages'])
    async def cursed(self, ctx):
        sub = await self.bot.handler.get_post("cursedimages")
        if sub["nsfw"] and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"{sub['title']}\n{sub['url']}")

    @commands.command()
    async def ooer(self, ctx):
        sub = await self.bot.handler.get_post("Ooer")
        if sub["nsfw"] and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"{sub['title']}\n{sub['url']}")
    
    @commands.command(aliases=['surreal', 'surrealmemes'])
    async def surrealmeme(self, ctx):
        sub = await self.bot.handler.get_post("surrealmemes")
        if sub["nsfw"] and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"{sub['title']}\n{sub['url']}")

    @commands.command(aliases=['imsorryjon', 'imsorryjohn'])
    async def imsorry(self, ctx):
        sub = await self.bot.handler.get_post("imsorryjon")
        if sub["nsfw"] and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"{sub['title']}\n{sub['url']}")


def setup(bot):
    bot.add_cog(ImageFetcher(bot))
