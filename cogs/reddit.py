import asyncio
import logging
import random
import discord
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


    async def get_post(self, guild_id: int, subreddit: str) -> Post:
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
                        if any(post["data"]["url"] == x.url for x in self.posts):
                            post = list(filter(lambda a: a.url == data["data"]["url"], self.posts))[0]
                            post.up = post["data"]["ups"]
                            post.down = post["data"]["downs"]
                            continue
                        
                        if not "url" in post["data"]:
                            continue
                        if not any(post["data"]["url"].endswith(x) for x in accepted_extensions):
                            continue

                        obj = Post(
                            title=post["data"]["title"],
                            url=post["data"]["url"],
                            subreddit=subreddit,
                            nsfw=post["data"]["over_18"],
                            up=post["data"]["ups"],
                            down=post["data"]["downs"]
                        )
                        self.posts.append(obj)
                        log.debug("%s: %r", subreddit, obj)
                    posts = list(filter(lambda a: not guild_id in a.guild_ids and a.subreddit == subreddit, self.posts))
                    log.debug("%s: %d", subreddit, len(posts))
                    try:
                        post = random.choice(posts)
                        log.debug("success")
                    except IndexError:
                        post = random.choice(list(filter(lambda a: a.subreddit == subreddit, self.posts)))
                        log.debug("disregarding if used or not")
                        

                    post.guild_ids.add(guild_id)
                    log.debug("get post: %r", post)
                    return post
        else:
            log.debug("reached")
            post = random.choice(filtered)
            post.guild_ids.add(guild_id)
            return post


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.handler = SubredditHandler(self.bot)
        
        cmds = [
            {"name" : "hmmm", "aliases" : ["hm", "hmm", "hmmmm", "hmmmmmm"]},
            {"name" : "cursedimages", "aliases" : ["cursedimage", "cursed"]},
            {"name" : "ooer", "aliases" : []},
            {"name" : "surrealmeme", "aliases" : ["surreal", "surrealmemes"]},
            {"name" : "imsorry", "aliases" : ["imsorryjon", "imsorryjohn"]}
        ]
        for row in cmds:
            command = commands.Command(
                func=Reddit._sub_handler,
                name=row["name"],
                aliases=row["aliases"],
                help=f"Fetch a post from the r/{row['name']} subreddit"
            )
            command.cog = self
            self.bot.add_command(command)


    async def _sub_handler(self, ctx):
        if not ctx.channel.is_nsfw() and ctx.guild.id in self.bot.nsfw_required:
            raise commands.NSFWChannelRequired(ctx.channel)
        try:
            post = await self.handler.get_post(ctx.guild.id, ctx.command.qualified_name)
            embed = discord.Embed(
                title=post.title,
                color=discord.Color(0x36393E)
            )
            embed.set_image(url=post.url)
            embed.set_footer(text=f"\U00002b06 {post.up} \U00002b07 {post.down}")
            await ctx.send(embed=embed)
        except (UnhandledStatusCode, SubredditNotFound) as error:
            await ctx.send(error)
           
    async def cog_check(self, ctx):
        return ctx.guild is not None    
    
    @commands.has_permissions(manage_guild=True)
    @commands.command(
        name="toggle-nsfw", 
        help="A command to turn on or off the requirement of reddit commands being executed in only NSFW channels"
    )
    async def toggle_nsfw(self, ctx):
        toggled_state = await self.bot.db.fetchval("SELECT toggle_nsfw($1);", ctx.guild.id)
        if toggled_state == 1:
            await ctx.send(":unlock: The NSFW channel requirement for reddit commands has been removed")
            self.bot.nsfw_required.discard(ctx.guild.id)
        else:
            await ctx.send(":lock: The NSFW channel requirement for reddit commands has been enabled")
            self.bot.nsfw_required.add(ctx.guild.id)
            

def setup(bot):
    bot.add_cog(Reddit(bot))
