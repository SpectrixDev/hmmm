import asyncio
import random
import time

import aiohttp
import discord

from datetime import datetime
from discord.ext import commands


class General:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"**:ping_pong: {round(self.bot.latency * 1000)}ms**")

    @commands.command()
    async def help(self, ctx):
        e = discord.Embed(color=discord.Color(value=0xc904e2))
        e.set_author(name="Command documentation")
        e.add_field(name="??hmmm", value="- Sends an oddly funny image, freshly stashed. You can also use **??hm, ??hmm, ??hmmmm for aliases.**\n")
        e.add_field(name="??cursed", value="- [**NSFW**] Sends you a cursed image. You never know what you're gonna get. Could be weird, dark, funny, or disgusting... **NSFW channel required.**\n")
        e.add_field(name="??imsorryjon", value="- Sends images of innocent cartoon characters, usually Garfield, but with a dark twist. A **very**, dark twist...")
        e.add_field(name="??surrealmeme", value="- Sends a surreal meme. Surreal memes are memes that make no logical sense, and are somehow amusing.")
        e.add_field(name="??ooer", value="- Sends completely *n͘͞or҉͡ḿ́al̷͏ images* from a completely n̢̢͠o̢̢͡͞҉ŕ̴͘͟m̨҉̨a͢͞͏̀l̢̕͠͝ place...  ***l e m o n***")
        e.add_field(name="Other commands", value="??ping, ??uptime, ??help, ??server")
        e.set_footer(text='"Much more coming soon. I think... but then again I question my sanity every time I write another line of code..." - Spectrix')
        e.set_thumbnail(url="https://styles.redditmedia.com/t5_2qq6z/styles/communityIcon_ybmhghdu9nj01.png")
        await ctx.send(embed=e)

    @commands.command()
    async def uptime(self, ctx):
        uptime = datetime.utcnow() - self.bot.uptime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")



    @commands.command(aliases=['support'])
    async def server(self, ctx):
        try:
            await ctx.author.send("**https://discord.gg/Kghqehz**\n*Here's my official server!*")
            message = await ctx.send("**I sent you my server invite in your DMs :mailbox_with_mail:**")
        except Exception:
            message = await ctx.send(f"**{ctx.author.mention} https://discord.gg/Kghqehz/**\n*Here's my official server!*")
        await message.add_reaction("🤔")

    @commands.command()
    async def invite(self, ctx):
        url = discord.utils.oauth_url(self.bot.user.id, discord.Permissions(321600))
        await ctx.send(f"**{url}** Here's my invite!")
        

def setup(bot):
    bot.add_cog(General(bot))
