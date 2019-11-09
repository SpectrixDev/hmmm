import logging
import discord
from discord.ext import commands
from utils.formats import *  # pylint: disable=wildcard-import

log = logging.getLogger(__name__)



class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook = bot.webhook

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.update()
        

        bots = sum(1 for x in guild.members if x.bot)
        humans = sum(1 for x in guild.members if not x.bot)
        members = guild.member_count

        message = GUILD_STATUS_MESSAGE.format(
            type="Joined", 
            guild=guild, 
            bots=bots,
            humans=humans
        )
        log.info(message)
        await self.webhook.send("```\n%s\n```" % message)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        bot_count = sum(1 for x in guild.members if x.bot)
        human_count = sum(1 for x in guild.members if not x.bot)
        member_count = guild.member_count
        message = GUILD_STATUS_MESSAGE.format(
            type="Lefted", 
            guild=guild, 
            bots=bots,
            humans=humans
        )
        log.info(message)
        await self.webhook.send("```\n%s\n```" % message)
        await self.bot.update()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.guild:
            MESSAGE = GUILD_COMMAND_MESSAGE.format(ctx=ctx)
        else:
            MESSAGE = COMMAND_MESSAGE.format(ctx=ctx)
        self.bot.command_usage[ctx.command.qualified_name] += 1
        log.info(MESSAGE)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, "original", error)

        ignored = (
            commands.UserInputError,
            commands.CommandNotFound,
            commands.MissingPermissions,
            commands.BotMissingPermissions,
            commands.NotOwner
        )

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.NSFWChannelRequired):
            # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.is_nsfw
            return await ctx.send("You can only use this command in a NSFW only channel!")

        if ctx.guild:
            payload = GUILD_MESSAGE.format(ctx=ctx, error=error)

        else:
            payload = DM_MESSAGE.format(ctx=ctx, error=error)

        log.error(payload)
        await self.webhook.send("```fix\n%s\n```" % payload)
        
def setup(bot):
    bot.add_cog(EventHandler(bot))
