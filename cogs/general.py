import logging
import platform
import os
from datetime import datetime, timedelta

import discord
import humanize
from discord.ext import commands

import psutil


log = logging.getLogger(__name__)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Get the WS latency of the bot")
    async def ping(self, ctx):
        await ctx.send(f"**:ping_pong: {round(self.bot.latency * 1000, 3)}ms**")

    @commands.command(help="Shows the current uptime of the bot")
    async def uptime(self, ctx):
        uptime = datetime.now() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")

    @commands.command(
        aliases=['support', 'guild'],
        help="Receive an invite to the support server"
    )
    async def server(self, ctx):
        await ctx.send("<https://discord.gg/Kghqehz>\nHere's my support server")

    @commands.command(
        aliases=["i", "inv"],
        help="Get an link to invite the bot to other guilds!"
    )
    async def invite(self, ctx):
        url = discord.utils.oauth_url(self.bot.user.id, discord.Permissions(8))
        embed = discord.Embed(title=str(self.bot.user), color=discord.Color.dark_blue())
        embed.description = f"[Click here]({url}) to invite {self.bot.user.name} to your guild!"
        await ctx.send(embed=embed)

    @commands.command(
        aliases=["about"],
        help="Get some information about the bot and its environment"
    )
    async def info(self, ctx):

        usage = sum(v for k, v in self.bot.command_usage.items())
        proc = psutil.Process(os.getpid())

        embed = discord.Embed(
            title=str(self.bot.user),
            color=discord.Color(value=0xc904e2)
        )

        embed.description = "\n".join([
            self.bot.description,
            f"{usage:,d} commands has been executed since last boot\n",
            f"[Upvote](https://top.gg/bot/{self.bot.user.id}/vote)",
            f"[Support](https://discord.gg/Kghqehz)",
            f"[Repository](https://github.com/SpectrixOfficial/hmmm)",
            f"[VPS Referral Link](https://billing.galaxygate.net/aff.php?aff=58)"
        ])

        counts = [
            f"I'm in {len(self.bot.guilds):,d} guilds",
            f"Seeing {len(set(self.bot.get_all_channels())):,d} channels",
            f"Listening to {len(set(self.bot.get_all_members())):,d} users"
        ]

        os_info = [
            f"OS: `{platform.platform()}`",
            f"CPU Usage: {psutil.cpu_percent()}%",
            f"CPU Cores: {psutil.cpu_count()}",
        ]
        stats = [
            f"Been running since {humanize.naturaltime(self.bot.uptime)}",
            f"Using {humanize.naturalsize(proc.memory_full_info().rss)} physical memory",
            f"Using discord.py {discord.__version__} and Python {platform.python_version()}",
        ]
        embed.add_field(name="Runtime", value="\n".join(stats), inline=False)
        embed.add_field(name="Host", value="\n".join(os_info))
        embed.add_field(name="Counts", value="\n".join(counts))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
