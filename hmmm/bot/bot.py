import logging
import os
import pathlib
from collections import Counter
from datetime import datetime

import aiohttp
import asyncpg
import discord
from discord.ext import commands

from dotenv import load_dotenv
from utils.objects import LogFormatter

import ujson as json



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
    return [f"<@{bot.user.id}> ", os.getenv("PREFIX")]


class Hmmm(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            description="A bot created for very very weird stuff posted on various subreddits!"  # nopep8
        )
        owners = os.getenv("OWNERS")
        self.owners = set(map(int, owners.split(',')) if owners else {})
        self.uptime = datetime.now()
        self.debug_mode = os.getenv("DEBUG") == "True"
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

    async def on_connect(self):
        log.info("BOOT @ %s", FILENAME)
        log.info("Connecting to discord...")

        self.session = aiohttp.ClientSession(json_serialize=json.dumps)
        adapter = discord.AsyncWebhookAdapter(self.session)
        self.webhook = discord.Webhook.from_url(
            os.getenv("WEBHOOK_URL"), adapter=adapter)

        try:
            credentials = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "database": os.getenv("DB_NAME"),
                "password": os.getenv("DB_PASSWORD"),
            }
            self.db = await asyncpg.create_pool(**credentials)
            with open("sql/schema.sql") as f:
                await self.db.execute(f.read())
                log.info("Executed SQL scheme")

            for guild in await self.db.fetch("SELECT * FROM nsfw_opted"):
                self.nsfw_required.add(guild["guild_id"])
        except ConnectionRefusedError:
            log.critical("db connection refused, stopping bot")
            await self.logout()
            return

        extensions = [x.as_posix().replace("/", ".").replace(".py", "")
                      for x in pathlib.Path("cogs").iterdir() if x.is_file()]

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
            name=f"{os.getenv('PREFIX')}help | {len(self.guilds)} guilds.",
            url="https://www.twitch.tv/SpectrixYT"
        )
        await self.change_presence(activity=activity)

        if os.getenv("DBL_TOKEN") and not self.debug_mode:
            payload = {"server_count": len(self.guilds)}
            headers = {"Authorization": os.getenv("DBL_TOKEN")}
            url = "https://top.gg/api/bots/%d/stats" % self.user.id
            async with self.session.post(url, json=payload, headers=headers) as resp:  # nopep8
                try:
                    data = await resp.json()
                    log.info("Recieved %s %s %d %s", resp.method,
                             resp._url, resp.status, data)
                except (TypeError, ValueError):
                    log.info("Recieved %s %s %d", resp.method,
                             resp._url, resp.status)

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
    load_dotenv()
    hmm = Hmmm()
    hmm.run(os.getenv("DISCORD_TOKEN"))
