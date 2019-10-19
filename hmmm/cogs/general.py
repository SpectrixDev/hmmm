import asyncio
import random
import time
import logging
import aiohttp
import discord
import platform
from datetime import datetime
from discord.ext import commands

log = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"**:ping_pong: {round(self.bot.latency * 1000, 3)}ms**")

    @commands.command(name="help")
    async def _help(self, ctx):
        prefixes = self.bot.command_prefix(ctx.bot, ctx.message)
        e = discord.Embed(color=discord.Color(value=0xc904e2), description=f"Prefixes: {', '.join(prefixes)}")
        e.set_author(name="Command documentation")
        e.add_field(name=f"hmmm", value="- Sends an oddly funny image, freshly stashed. You can also use **hm, hmm, hmmmm for aliases.**")
        e.add_field(name="cursed", value="- Sends you a cursed image. You never know what you're gonna get. Could be weird, dark, funny, or disgusting...")
        e.add_field(name="imsorryjon", value="- Sends images of innocent cartoon characters, usually Garfield, but with a dark twist. A **very**, dark twist...")
        e.add_field(name="surrealmeme", value="- Sends a surreal meme. Surreal memes are memes that make no logical sense, and are somehow amusing.")
        e.add_field(name="ooer", value="- Sends completely *n͘͞or҉͡ḿ́al̷͏ images* from a completely n̢̢͠o̢̢͡͞҉ŕ̴͘͟m̨҉̨a͢͞͏̀l̢̕͠͝ place...  ***l e m o n***")
        e.add_field(name="Other commands", value="ping, uptime, help, info, support, invite, healthcheck")
        e.set_footer(text='"Much more coming soon. I think... but then again I question my sanity every time I write another line of code..." - Spectrix')
        e.set_thumbnail(url=str(self.bot.user.avatar_url))
        await ctx.send(embed=e)
 
    @commands.command()
    async def uptime(self, ctx):
        uptime = datetime.utcnow() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")



    @commands.command(aliases=['support', 'guild'])
    async def server(self, ctx):
         await ctx.send(f"{ctx.author.mention} <https://discord.gg/Kghqehz>\nHere's my support server")
        

    @commands.command()
    async def invite(self, ctx):
        url = discord.utils.oauth_url(self.bot.user.id, discord.Permissions(8))
        embed = discord.Embed(title="Invites", color=discord.Color.dark_blue())
        embed.description = f"[Click here]({url}) to invite {self.bot.user.name} to your server!"
        await ctx.send(embed=embed)


    @commands.command()
    async def info(self, ctx):
        
        uptime = datetime.utcnow() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        uptime = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
        os = platform.platform()
        cmd_usage = sum(v for k,v in self.bot.command_usage.items())
        
        description = [
            self.bot.description + f", {cmd_usage} commands has been executed since last boot\n",
            f"[Upvote](https://top.gg/bot/{self.bot.user.id}/vote)",
            f"[Referral Link](https://billing.galaxygate.net/aff.php?aff=58)",
            f"[Source code](https://github.com/SpectrixOfficial/hmmm)",
            f"[Support Server](https://discord.gg/Kghqehz)"
        ]
        embed = discord.Embed(
            title="Bot info",
            description="\n".join(description),
            color=discord.Color(value=0xc904e2)
        )
        stats = [
            f"I'm in {len(self.bot.guilds)} guilds",
            f"Seeing {len(set(self.bot.get_all_channels())):,d} channels",
            f"Listening to {len(set(self.bot.get_all_members())):,d} users"

        ]
        embed.add_field(name="Host", value=os, inline=False)
        embed.add_field(name="Uptime", value=uptime, inline=False)
        embed.add_field(name="Statistics", value="\n".join(stats))
        await ctx.send(embed=embed)

        
        
def setup(bot):
    bot.add_cog(General(bot))
