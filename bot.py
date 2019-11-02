import logging
import os
import pathlib
from collections import Counter
from datetime import datetime

import aiohttp
import asyncpg
import discord
from discord.ext import commands

from utils.objects import LogFormatter

try:
    import ujson as json
except ImportError:
    import json




if not os.path.exists("logs"):
    os.mkdir("logs")

FILENAME = datetime.utcnow().strftime("logs/%Y-%m-%d_%H-%M-%S.log")
log = logging.getLogger("cogs")
log.setLevel(logging.DEBUG)


l = logging.FileHandler(FILENAME, "w", "utf-8")
s = logging.StreamHandler()
s.setFormatter(LogFormatter())
l.setFormatter(LogFormatter(use_ansi=False))
log.handlers = [l, s]


def get_prefix(bot, _message):
    return [f"<@{bot.user.id}> ", bot.config.get("prefix")]

class CustomContext(commands.Context):

    async def send(self, *args, **kwargs):
        if not self.guild.me.permissions_in(self.channel).send_messages:
            raise commands.BotMissingPermissions(["send_messages"])

        return await super().send(*args, **kwargs)

class Hmmm(commands.AutoShardedBot):
    def __init__(self, config: dict):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            description="A bot created for very very weird stuff posted on various subreddits!"  # nopep8
        )
        self.config = config
        self.owners = set(config.get("owners", {}))
        self.uptime = datetime.now()
        self.debug_mode = config.get("debug_mode", True)
        self.command_usage = Counter()
        self.db = None
        self.nsfw_required = set()



    async def is_owner(self, user):
        return user.id in self.owners or await super().is_owner(user)


    async def on_ready(self):
        await self.update()
        log.info("%s is ready", self.user)
        log.info("ID: %d", self.user.id)
        log.info("Created At:  %s", self.user.created_at)
        log.info("User Count: %d", len(set(self.get_all_members())))
        log.info("Channel Count: %d", len(set(self.get_all_channels())))
        log.info("Guild Count: %d", len(self.guilds))
        log.info("Debug Mode: %s", str(self.debug_mode))


    async def get_context(self, message, * , cls=commands.Context):
        return await super().get_context(message, cls=CustomContext)



    async def on_connect(self):
        log.info("BOOT @ %s", FILENAME)
        log.info("Connecting to discord...")

        self.session = aiohttp.ClientSession(json_serialize=json.dumps)
        adapter = discord.AsyncWebhookAdapter(self.session)
        self.webhook = discord.Webhook.from_url(self.config["webhook_url"], adapter=adapter)

        try:
            self.db = await asyncpg.create_pool(**self.config["database"])
            with open("schema.sql") as f:
                await self.db.execute(f.read())
                log.info("Executed SQL scheme")
            
            for guild in await self.db.fetch("SELECT * FROM nsfw_opted"):
                self.nsfw_required.add(guild["guild_id"])
        except ConnectionRefusedError:
            log.critical("db connection refused, stopping bot")
            await self.logout()
            return


        extensions = [x.as_posix().replace("/", ".").replace(".py", "") for x in pathlib.Path("cogs").iterdir() if x.is_file()]

        extensions.append("jishaku")

        for ext in extensions:
            try:
                self.load_extension(ext)
                log.info("Loaded extension: %s", ext)

            except commands.ExtensionFailed:
                log.error("Extension %s failed to load: ", ext, exc_info=True)

            except commands.ExtensionNotFound:
                log.warning("Extension %s cannot be found", ext)

            except commands.NoEntryPointError:
                log.warning("Extension %s has no setup function", ext)

    async def update(self):
        activity = discord.Activity(
            type=1,
            name=f"{self.config['prefix']}help | {len(self.guilds)} guilds.",
            url="https://www.twitch.tv/SpectrixYT"
        )
        await self.change_presence(activity=activity)

        if self.config.get("dbl_token") and not self.debug_mode:
            payload = {"server_count": len(self.guilds)}
            headers = {"Authorization": self.config["dbl_token"]}
            url = "https://top.gg/api/bots/%d/stats" % self.user.id
            async with self.session.post(url, json=payload, headers=headers) as resp:  # nopep8
                try:
                    data = await resp.json()
                    log.info("Recieved %s %s %d %s", resp.method, resp._url, resp.status, data)
                except (TypeError, ValueError):
                    log.info("Recieved %s %s %d", resp.method, resp._url, resp.status)


    async def logout(self):
        log.debug("logout() got called, logging out and cleaning up tasks")
        try:
            await self.session.close()
            if self.db:
                await self.db.close()
        except (RuntimeError, AttributeError):
            pass
        return await super().logout()




if __name__ == "__main__":
    with open("config.json") as file:
        configuration = json.load(file)
    hmm = Hmmm(config=configuration)
    hmm.run(configuration["bot_token"])
