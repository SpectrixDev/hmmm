import asyncio
import logging
import random
from discord.ext import commands

from utils.errors import SubredditNotFound, UnhandledStatusCode
from utils.objects import Post

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
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.posts = []


    async def get_post(self, guild_id: int, subreddit: str):
        filtered = list(filter(lambda a: not guild_id in a.guild_ids and a.subreddit == subreddit, self.posts))
        log.debug(len(filtered))
        if len(filtered) == 0:
            attempts = 0
            while attempts < 5:
                attempts += 1
                async with self.bot.session.get("https://reddit.com/r/%s/new.json?sort=top&limit=500" % subreddit) as resp:
                    if resp.status == 429:
                        log.warning("Site has responded with a %d %s", resp.status, resp.reason)
                        await asyncio.sleep(10)
                        continue
                    if resp.status != 200:
                        raise UnhandledStatusCode(resp.status, resp._url, resp.reason)

                    data = await resp.json()

                    if len(data["data"]["children"]) == 0:
                        raise SubredditNotFound(subreddit, resp.status)
                    
                    for post in data["data"]["children"]:
                        if not "url" in post["data"] or any(post["data"]["url"] == x.url for x in self.posts):
                            continue
                        if not any(post["data"]["url"].endswith(x) for x in accepted_extensions):
                            continue

                        obj = Post(
                            title=post["data"]["title"],
                            url=post["data"]["url"],
                            subreddit=subreddit,
                            is_nsfw=post["data"]["over_18"]
                        )
                        self.posts.append(obj)
                    posts = list(filter(lambda a: not guild_id in a.guild_ids and a.subreddit == subreddit, self.posts))
                    post = random.choice(posts)
                    post.guild_ids.add(guild_id)
                    log.debug("get post: %r", post)
                    return post
        else:
            post = random.choice(filtered)
            post.guild_ids.add(guild_id)
            return post


class Reddit(commands.Cog, name="Reddit commands"):
    def __init__(self, bot):
        self.bot = bot
        self.handler = SubredditHandler(self.bot)
        self._commands = {
            "hmmm" : ["hm", "hmm", "hmmmm", "hmmmmmm"],
            "cursed" : ["cursedimage", "cursedimages"],
            "ooer" : [],
            "surrealmeme" : ["surreal", "surrealmemes"],
            "imsorry" : ["imsorryjon", "imsorryjohn"]
        }
        for sub, alias in self._commands.items():
            cmdobj = commands.Command(
                func=self._handler,
                name=sub,
                aliases=alias,
                cog=self
            )
            self.bot.add_command(cmdobj)


    async def _handler(self, ctx):
        if not ctx.channel.is_nsfw() and (ctx.bot.settings.get(ctx.guild.id) is None or ctx.bot.settings[ctx.guild.id]["allow_nsfw"] is False):
            raise commands.NSFWChannelRequired(ctx.channel)

        try:
            post = await self.handler.get_post(ctx.guild.id, ctx.command.qualified_name)
            print(post)
            await ctx.send(f"**{post.title}**\n{post.url}")
        except SubredditNotFound as error:
            await ctx.send(error)
        except UnhandledStatusCode as error:
            await ctx.send(error)
            


def setup(bot):
    bot.add_cog(Reddit(bot))
    