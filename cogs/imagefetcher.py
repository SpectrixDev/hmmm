import discord, datetime, time, aiohttp, asyncio, random
from discord.ext import commands
from random import randint
from random import choice
from urllib.parse import quote_plus
from collections import deque

acceptableImageFormats = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]
memeHistory = deque()

async def getSub(self, ctx, sub):
        """Get stuff from requested sub"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.reddit.com/r{sub}/hot.json?limit=100") as response:
                request = await response.json()

        attempts = 1
        while attempts < 5:
            if 'error' in request:
                print("failed request {}".format(attempts))
                await asyncio.sleep(2)
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=100") as response:
                        request = await response.json()
                attempts += 1
            else:
                index = 0

                for index, val in enumerate(request['data']['children']):
                    if 'url' in val['data']:
                        url = str(val['data']['url'])
                        nsfw = val['data']['over_18']
                        title = f"**{str(val['data']['title'])}**"
                        pinned = val['data']['stickied']
                        print(title)
                        urlLower = url.lower()
                        accepted = False
                        for j, v, in enumerate(acceptableImageFormats): #check if it's an acceptable image
                            if v in urlLower:
                                accepted = True
                            elif pinned == True:
                                accepted = False
                            elif nsfw == True:
                                if ctx.channel.is_nsfw():
                                    accepted = True
                                else:
                                    accepted = False
                                    await ctx.send("**:no_entry: Oops! Couldn't send this image, it was marked nsfw. Mark this channel as nsfw to view nsfw messages.**")
                            else:
                                accepted == True
                        if accepted:
                            if (f"**{title}**" + '\n' + url) not in memeHistory:
                                if title != "**hmmm**":
                                    memeHistory.append(title + '\n' + url)
                                else:
                                    title = ''
                                    memeHistory.append(title + '\n' + url)
        
                                if len(memeHistory) > 68: #limit size
                                    memeHistory.popleft() #remove the oldest
                                break #done with this loop, can send image

                await ctx.send(memeHistory[len(memeHistory) - 1]) #send the last image
                return
        await ctx.send("_{}! ({})_".format(str(request['message']), str(request['error'])))

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

def setup(bot):
    bot.add_cog(imagefetcher(bot))