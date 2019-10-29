import discord
import logging
import asyncio
import aiohttp
from discord.ext import commands
from aiohttp import web


log = logging.getLogger(__name__)

class Webserver(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self._webhook = discord.AsyncWebhookAdapter(self.bot.session)
        self.app.add_routes([
            web.post(bot.config["server"]["path"], self.vote_handler)
        ])
        self._runner = web.AppRunner(self.app)
        self._server = None

    def cog_unload(self):
        asyncio.run_coroutine_threadsafe(self._server.stop(), loop=self.bot.loop)

    async def start(self):
        await self._runner.setup()
        self._server = web.TCPSite(self._runner, self.bot.config["server"]["host"], self.bot.config["server"]["port"])
        await self._server.start()


    async def stop(self):
        await self._server.stop()

    async def vote_handler(self, request):
        if request.headers.get("Authorization") == self.bot.config["server"]["auth"]:

            data = await request.json()
            user = self.bot.get_user(int(data["user"]))
            if user is None:
                user = data["user"]

            embed = discord.Embed(
                title="Somebody has voted!",
                description=f"Thanks {user.mention} for voting for me!"
            )

            await self._webhook.request("POST", self.bot.config["server"]["webhook"], {"embed" : embed.to_dict()})






def setup(bot):
    ws = Webserver(bot)
    bot.loop.create_task(ws.start())
    bot.add_cog(ws)
