import asyncio
import datetime
import discord
import logging
import random
from collections import deque
from discord.ext import commands
from cogs.objects import UnhandledStatusCode, SubredditNotFound

log = logging.getLogger(__name__)


        


class ImageFetcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['hm', 'hmm', 'hmmmm', 'hmmmmm'])
    async def hmmm(self, ctx):
        async with ctx.channel.typing():
            try:
                sub = await self.bot.handler.get_post("hmmm")
            except UnhandledStatusCode as error:
                log.error(error)
                return await ctx.send(error)

            if sub.nsfw and not ctx.channel.is_nsfw():
                raise commands.NSFWChannelRequired(ctx.channel)
            else:
                if len(sub.title) == 0:
                    await ctx.send(sub.url)
                else:
                    await ctx.send(f"**{sub.title[:100]}**\n{sub.url}")
    
    @commands.command(aliases=['cursedimage', 'cursedimages'])
    async def cursed(self, ctx):
        try:
            sub = await self.bot.handler.get_post("cursedimages")
        except UnhandledStatusCode as error:
            log.error(error)
            return await ctx.send(error)

        if sub.nsfw and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"**{sub.title[:100]}**\n{sub.url}")

    @commands.command()
    async def ooer(self, ctx):
        try:
            sub = await self.bot.handler.get_post("Ooer")
        except UnhandledStatusCode as error:
            log.error(error)

            return await ctx.send(error)

        if sub.nsfw and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"**{sub.title[:100]}**\n{sub.url}")

    @commands.command(aliases=['surreal', 'surrealmemes'])
    async def surrealmeme(self, ctx):
        try:
            sub = await self.bot.handler.get_post("surrealmemes")
        except UnhandledStatusCode as error:
            log.error(error)
            return await ctx.send(error)

        if sub.nsfw and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"**{sub.title[:100]}**\n{sub.url}")

    @commands.command(aliases=['imsorryjon', 'imsorryjohn'])
    async def imsorry(self, ctx):
        try:
            sub = await self.bot.handler.get_post("imsorryjon")
        except UnhandledStatusCode as error:
            log.error(error)
            return await ctx.send(error)

        if sub.nsfw and not ctx.channel.is_nsfw():
            raise commands.NSFWChannelRequired(ctx.channel)
        else:
            await ctx.send(f"**{sub.title[:100]}**\n{sub.url}")

def setup(bot):
    bot.add_cog(ImageFetcher(bot))
