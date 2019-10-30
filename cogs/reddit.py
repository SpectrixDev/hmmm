import logging
from discord.ext import commands
from cogs.handler import DM_MESSAGE, GUILD_MESSAGE
from utils.errors import SubredditNotFound, UnhandledStatusCode

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

    async def getPost(self, subreddit: str):
        pass #wq





class Reddit(commands.Cog, name="Reddit commands"):
    def __init__(self, bot):
        self.bot = bot
        self.handler = SubredditHandler(self.bot)
        self._commands = {
            "hmmm" : ["hm", "hmm", "hmmm", "hmmmm", "hmmmmmm"],
            "cursed" : ["cursedimage", "cursedimages"],
            "ooer" : [],
            "surrealmeme" : ["surreal", "surrealmemes"],
            "imsorry" : ["imsorryjon", "imsorryjohn"]
        }
        for sub, alias in self._commands.items():
            cmdobj = commands.Command(
                func=self._command_handler,
                name=sub,
                aliases=alias,
                cog=self
            )
            self.bot.add_command(cmdobj)


    async def _command_handler(self, ctx):
        if ctx.bot.settings.get(ctx.guild.id)
        try:
            post = await self.handler.get_post(ctx.command.qualified_name)

        except SubredditNotFound as error:
            await ctx.send(error)
        except UnhandledStatusCode as error:
            await ctx.send(error)




def setup(bot):
    bot.add_cog(Reddit(bot))
