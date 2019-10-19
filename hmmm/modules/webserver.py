import discord
import logging
import asyncio
from discord.ext import commands
from aiohttp import web



log = logging.getLogger(__name__)

class Webserver:

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self._runner = web.AppRunner(self.app)
        self._server = None

    async def start(self):
        self._webhook = discord.AsyncWebhookAdapter(self.bot.session)
        await self._runner.setup()
        self._server = web.TCPSite(self._runner, self.bot.config["server"]["host"], self.bot.config["server"]["port"])
        await self._server.start()

    async def stop(self):
        await self._runner.cleanup()
    
    async def vote_handler(self, request):
        if request.headers.get("Authorization") == self.bot.config["server"]["auth"]:   
            log.debug("Hiiiiiii dbl")
            data = await request.json()
            await self._webhook.request("POST", self.bot.config["server"]["webhook"], {"content" : str(data)})
        




def setup(bot):
    bot.add_cog(Webserver(bot))