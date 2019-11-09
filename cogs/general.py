import logging
import platform
import os
from datetime import datetime, timedelta

import discord
import humanize
from discord.ext import commands

import psutil
import asyncpg


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

    @commands.command(aliases=["about"], help='Get some information about the bot and its environment')
    async def info(self, ctx):

        embed = discord.Embed(title=str(self.bot.user), color=discord.Color(value=0xc904e2))
        proc = psutil.Process()
        usage = sum(v for k, v in self.bot.command_usage.items())

        embed.description = "\n".join([
            self.bot.description,
            f'{usage:,d} commands has been executed since last boot\n',
            f'[Upvote](https://top.gg/bot/{self.bot.user.id}/vote)',
            f'[Support](https://discord.gg/Kghqehz)',
            f'[Repository](https://github.com/SpectrixOfficial/hmmm)',
            f'[VPS Referral Link](https://billing.galaxygate.net/aff.php?aff=58)'
        ])

        counts = (
            f"I'm in {len(self.bot.guilds):,d} guilds",
            f'Seeing {len(set(self.bot.get_all_channels())):,d} channels',
            f'Listening to {len(set(self.bot.get_all_members())):,d} users'
        )
        os_info = (
            f'OS: `{platform.platform()}`',
            f'CPU Usage: {psutil.cpu_percent()}%',
            f'CPU Cores: {psutil.cpu_count()}',
        )
        stats = (
            f'Been running since {humanize.naturaltime(self.bot.uptime)}',
            f'Using {humanize.naturalsize(proc.memory_full_info().rss)} physical memory',
            f'Using discord.py {discord.__version__} and Python {platform.python_version()}',
        )
        embed.add_field(name="Runtime", value="\n".join(stats), inline=False)
        embed.add_field(name="Host", value="\n".join(os_info))
        embed.add_field(name="Counts", value="\n".join(counts))
        await ctx.send(embed=embed)

    @commands.group(name="prefix", invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx):
        embed = discord.Embed(
            title=ctx.guild.name,
            color=discord.Color(0x36393E),
            
        )
        
        embed.description = [
            f'1) {self.bot.user.mention}',
        ]
        if self.bot.prefixes.get(ctx.guild.id):
            embed.description.append(f'2) {self.bot.prefixes[ctx.guild.id]}')
        
        embed.description = "\n".join(embed.description)
        
        return await ctx.send(embed=embed)
        
    
    @prefix.command(name="set")
    @commands.has_permissions(manage_guild=True)                
    async def set_prefix(self, ctx, new_prefix: commands.clean_content = None):

        query = """
        INSERT INTO guild_settings (guild_id, prefix)
        VALUES ($1,$2)
        ON CONFLICT (guild_id)
        DO UPDATE
        SET prefix=$2
        """
        if new_prefix is None:
            await self.bot.db.execute(query, ctx.guild.id, None)
            self.prefixes.pop(ctx.guild.id)
            return await ctx.send("Prefix has been resetted")

        if len(new_prefix) > 15:
            return await ctx.send('Prefix length cannot be longer then 10 characters')

        await self.bot.db.execute(query, ctx.guild.id, new_prefix)
        if self.bot.prefixes.get(ctx.guild.id):
            await ctx.send(f'Successfully changed previous prefix `{self.bot.prefixes[ctx.guild.id]}` to `{new_prefix}`')
        else:
            await ctx.send(f'Changed prefix to `{new_prefix}`')
        self.bot.prefixes[ctx.guild.id] = new_prefix


def setup(bot):
    bot.add_cog(General(bot))
