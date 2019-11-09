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



BOOT = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FOLDER = pathlib.Path("logs")



log = logging.getLogger("cogs")


handler = logging.StreamHandler()
handler.setFormatter(LogFormatter())
log.addHandler(handler)


def get_prefix(bot, message):
    prefixes = [f"<@{bot.user.id}> "]
    if not message.guild:
        prefixes.append(bot.config.get("prefix"))
    else:
        if bot.prefixes.get(message.guild.id):
            prefixes.append(bot.prefixes[message.guild.id])
        else:
            prefixes.append(bot.config.get("prefix"))
        
    return prefixes

class Hmmm(commands.AutoShardedBot):
    def __init__(self, config: dict):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            description="A bot created for very very weird stuff posted on various subreddits."  # nopep8
        )
        self.config = config
        self.owners = set(config.get("owners", {}))
        self.uptime = datetime.now()
        self.debug_mode = config.get("debug_mode", True)
        self.command_usage = Counter()
        self.db = None
        self.prefixes = {}
        self.nsfw_restricted = set()
        if self.debug_mode is True:
            log.setLevel(logging.DEBUG)
        else:
            if not LOG_FOLDER.exists():
                LOG_FOLDER.mkdir() 
            
            file_handler = logging.FileHandler(f"logs/{BOOT}.log", "w", "utf-8")
            file_handler.setFormatter(LogFormatter(False))
            log.setLevel(logging.INFO)
            log.addFilter(file_handler)



    async def is_owner(self, user):
        return user.id in self.owners or await super().is_owner(user)


    async def on_ready(self):
        await self.update()
        log.info("--" * 15)
        log.info("%s is ready", self.user)
        log.info(" ")
        log.info("ID:            %d", self.user.id)
        log.info("Created_At:    %s", self.user.created_at)
        log.info("User Count:    %d", len(set(self.get_all_members())))
        log.info("Channels:      %d", len(set(self.get_all_channels())))
        log.info("Guilds:        %d", len(self.guilds))
        log.info("Debug:         %s", str(self.debug_mode))
        log.info("--" * 15)
    
    async def on_resumed(self):
        log.info("Resumed..")

    async def login(self, *args, **kwargs):
        log.info("BOOT @ %s", BOOT)
        log.info("Connecting to discord...")

        self.session = aiohttp.ClientSession(json_serialize=json.dumps)
        adapter = discord.AsyncWebhookAdapter(self.session)
        self.webhook = discord.Webhook.from_url(self.config["webhook_url"], adapter=adapter)

        try:
            self.db = await asyncpg.create_pool(**self.config["database"])
            with open("schema.sql") as f:
                try:
                    await self.db.execute(f.read())
                    log.info("Executed SQL schema")
                except asyncpg.SyntaxOrAccessError:
                    log.error("INVALID SQL SYNTAX ", exc_info=True)
                    return await self.logout()
                    
            
            for guild in await self.db.fetch("SELECT * FROM guild_settings"):
                if guild.get("prefix"):
                    self.prefixes.update({guild["guild_id"] : guild["prefix"] })
                if guild.get("nsfw_restricted"):
                    self.nsfw_restricted.add(guild["guild_id"])
                if self.debug_mode:
                    arguments = (guild["guild_id"], guild["prefix"], guild["nsfw_restricted"])
                    log.debug("Guild ID %d contents: PREFIX: %s NSFW_RESTRICTED: %s", *arguments)

        except ConnectionRefusedError:
            log.critical("Database connection refused, stopping bot")
            return await self.logout()


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
        await super().login(*args, **kwargs)

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


    async def close(self):
        log.debug("close() got called, cleaning up tasks")
        try:
            await self.session.close()
            await self.db.close()
        except (RuntimeError, AttributeError):
            pass
            
        await super().close()
    




if __name__ == "__main__":
    with open("config.json") as file:
        configuration = json.load(file)
    hmm = Hmmm(config=configuration)
    hmm.run(configuration["bot_token"])
