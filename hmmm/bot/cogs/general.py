import logging
import platform
from datetime import datetime

import discord
import humanize
from discord.ext import commands

log = logging.getLogger(__name__)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"**:ping_pong: {round(self.bot.latency * 1000, 3)}ms**")

    @commands.command()
    async def uptime(self, ctx):
        uptime = datetime.now() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")

    @commands.command(aliases=['support', 'guild'])
    async def server(self, ctx):
        await ctx.send("<https://discord.gg/Kghqehz>\nHere's my support server")

    @commands.command()
    async def invite(self, ctx):
        url = discord.utils.oauth_url(self.bot.user.id, discord.Permissions(8))
        embed = discord.Embed(title=str(self.bot.user),
                              color=discord.Color.dark_blue())
        embed.description = f"[Click here]({url}) to invite {self.bot.user.name} to your guild!"
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx):

        os = platform.platform()
        cmd_usage = sum(v for k, v in self.bot.command_usage.items())

        description = [
            self.bot.description +
            f", {cmd_usage:,d} commands has been executed since last boot\n",
            f"[Upvote](https://top.gg/bot/{self.bot.user.id}/vote)",
            f"[Support](https://discord.gg/Kghqehz)",
            f"[Referral Link](https://billing.galaxygate.net/aff.php?aff=58)",
            f"[Repository](https://github.com/SpectrixOfficial/hmmm)"
        ]
        embed = discord.Embed(
            title=str(self.bot.user),
            description="\n".join(description),
            color=discord.Color(value=0xc904e2)
        )
        stats = [
            f"I'm in {len(self.bot.guilds):,d} guilds",
            f"Seeing {len(set(self.bot.get_all_channels())):,d} channels",
            f"Listening to {len(set(self.bot.get_all_members())):,d} users"

        ]
        embed.add_field(name="Host", value=os, inline=False)
        embed.add_field(name="Uptime", value=humanize.naturaltime(
            self.bot.uptime), inline=False)
        embed.add_field(name="Statistics", value="\n".join(stats))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
