import asyncio
import datetime
import random
import time
import discord

from collections import deque
from random import choice, randint
from discord.ext import commands

allowed_image_extensions = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]


class ImageHandler:
    def __init__(self, bot , maxlen=400):
        self._items = deque(maxlen=maxlen)
        self.bot = bot

    

    async def fetcher(self)
    





class imagefetcher:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['hm', 'hmm', 'hmmmm', 'hmmmmm'])
    async def hmmm(self, ctx):
        async with ctx.channel.typing():
            await getSub(self, ctx, 'hmmm')
    
    @commands.is_nsfw()
    @commands.command(aliases=['cursedimage', 'cursedimages'])
    async def cursed(self, ctx):
        async with ctx.channel.typing():
            await getSub(self, ctx, 'cursedimages')
    
    @commands.command()
    async def ooer(self, ctx):
        async with ctx.channel.typing():
            await getSub(self, ctx, 'Ooer')
    
    @commands.command(aliases=['surreal', 'surrealmemes'])
    async def surrealmeme(self, ctx):
        async with ctx.channel.typing():
            await getSub(self, ctx, 'surrealmemes')
    
    @commands.command(aliases=['imsorryjon', 'imsorryjohn'])
    async def imsorry(self, ctx):
        async with ctx.channel.typing():
            await getSub(self, ctx, 'imsorryjon')

def setup(bot):
    bot.add_cog(imagefetcher(bot))
