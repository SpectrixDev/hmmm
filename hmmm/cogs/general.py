import asyncio
import random
import time

import aiohttp
import discord

from datetime import datetime
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"**:ping_pong: {round(self.bot.latency * 1000)}ms**")

    @commands.command(name="help")
    async def _help(self, ctx):
        prefixes = self.bot.command_prefix(ctx.bot, ctx.message)
        e = discord.Embed(color=discord.Color(value=0xc904e2), description=f"Prefix(es): {', '.join(prefixes)}")
        e.set_author(name="Command documentation")
        e.add_field(name=f"hmmm", value="- Sends an oddly funny image, freshly stashed. You can also use **hm, hmm, hmmmm for aliases.**")
        e.add_field(name="cursed", value="- [**NSFW**] Sends you a cursed image. You never know what you're gonna get. Could be weird, dark, funny, or disgusting...")
        e.add_field(name="imsorryjon", value="- Sends images of innocent cartoon characters, usually Garfield, but with a dark twist. A **very**, dark twist...")
        e.add_field(name="surrealmeme", value="- Sends a surreal meme. Surreal memes are memes that make no logical sense, and are somehow amusing.")
        e.add_field(name="ooer", value="- Sends completely *n͘͞or҉͡ḿ́al̷͏ images* from a completely n̢̢͠o̢̢͡͞҉ŕ̴͘͟m̨҉̨a͢͞͏̀l̢̕͠͝ place...  ***l e m o n***")
        e.add_field(name="Other commands", value="ping, uptime, help, support, invite, healthcheck")
        e.set_footer(text='"Much more coming soon. I think... but then again I question my sanity every time I write another line of code..." - Spectrix')
        e.set_thumbnail(url=str(self.bot.user.avatar_url))
        await ctx.send(embed=e)

    @commands.command()
    async def uptime(self, ctx):
        uptime = datetime.utcnow() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}s, {seconds}s")



    @commands.command(aliases=['support', 'guild'])
    async def server(self, ctx):
        message = await ctx.send(f"{ctx.author.mention} <https://discord.gg/Kghqehz>\nHere's my official server!")
        await message.add_reaction("🤔")

    @commands.command()
    async def invite(self, ctx):
        stable = discord.utils.oauth_url(self.bot.user.id, discord.Permissions(8))
        beta = discord.utils.oauth_url(631021131587125260, discord.Permissions(8))

        embed = discord.Embed(title="Invites", color=discord.Color.dark_blue())
        embed.description = "\n".join([
            f"[Main bot]({stable})",
            f"[Beta bot]({beta})"
        ])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
