import discord
import logging
import asyncio
import aiohttp
from discord.ext import commands
from aiohttp import web




log = logging.getLogger(__name__)

class Webserver:

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.app.add_routes([
            web.post(bot.config["server"]["path"], self.vote_handler)
        ])
        self._runner = web.AppRunner(self.app)
        self._server = None
        self._session = None

    async def start(self):
        self._session = aiohttp.ClientSession()
        self._webhook = discord.AsyncWebhookAdapter(self._session)
        await self._runner.setup()
        self._server = web.TCPSite(self._runner, self.bot.config["server"]["host"], self.bot.config["server"]["port"])
        await self._server.start()
        

    async def stop(self):
        if not self._session:
            raise RuntimeError("must call start() first")
        await self._runner.cleanup()
    
    async def vote_handler(self, request):
        if request.headers.get("Authorization") == self.bot.config["server"]["auth"]:   
            log.debug("Hiiiiiii dbl")
            data = await request.json()
            await self._webhook.request("POST", self.bot.config["server"]["webhook"], {"content" : str(data)})
        




def setup(bot):
    bot.add_cog(Webserver(bot))