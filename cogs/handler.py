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

        message = GUILD_STATUS_MESSAGE.format("Joined", guild, members, bots, humans)
        log.info(message)
        await self.webhook.send("```\n%s\n```" % message)

        if guild.system_channel:
            prefix = self.bot.config['prefix']
            embed = discord.Embed(color=discord.Color(value=0x36393e))
            embed.set_author(name="Confused? You should be, this bot makes no sense. Take this, it might help:")
            embed.add_field(name="Prefix", value="`%s`, or *mention me.*" % prefix)
            embed.add_field(name="Command help", value="%shelp" % prefix)
            embed.add_field(name="Support Server", value="[Join, it's fun here](https://discord.gg/Kghqehz)")
            embed.add_field(name="Upvote", value="[Click here](https://top.gg/bot/%d/vote)" % self.bot.user.id)
            embed.set_thumbnail(url=str(self.bot.user.avatar_url))
            embed.set_footer(text=f"Thanks to you, this monstrosity of a bot is now on {len(self.bot.guilds):,d} servers!", icon_url="https://media.giphy.com/media/ruw1bRYN0IXNS/giphy.gif")
            await guild.system_channel.send(content="**Hello gamers! Thanks for inviting me! :wave: **", embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        bot_count = sum(1 for x in guild.members if x.bot)
        human_count = sum(1 for x in guild.members if not x.bot)
        member_count = guild.member_count
        message = GUILD_STATUS_MESSAGE.format("Lefted", guild, member_count, bot_count, human_count)
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
            commands.BotMissingPermissions
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
        await ctx.send("Seems like an unhandled error has occured, my developer has been notified!")

def setup(bot):
    bot.add_cog(EventHandler(bot))
