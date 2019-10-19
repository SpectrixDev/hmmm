import discord
import logging
from discord.ext import commands
from aiohttp import web



log = logging.getLogger(__name__)

class Webserver(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self._runner = web.AppRunner(self.app)
        self._server = web.TCPSite(self._runner, bot.config["server"]["host"], bot.config["server"]["port"])
        self._webhook = discord.AsyncWebhookAdapter(self.bot.session)
        self.bot.loop.run_until_complete(self._runner.setup())
        self.bot.loop.run_until_complete(self._server.start())
    

    def cog_unload(self):
        if self._runner:
            self.bot.loop.run_until_complete(self._runner.cleanup())
    



    async def vote_handler(self, request):
        if request.headers.get("Authorization") == self.bot.config["server"]["auth"]:   
            log.debug("Hiiiiiii dbl")
            data = await request.json()
            await self._webhook.request("POST", self.bot.config["server"]["webhook"], {"content" : str(data)})
        




def setup(bot):
    bot.add_cog(Webserver(bot))