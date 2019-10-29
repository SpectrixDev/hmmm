import os
import zlib
import asyncio
import logging
import pathlib
import aiohttp
import asyncpg
import discord
from objects import LogFormatter
from collections import Counter
from datetime import datetime
from discord.ext import commands
try:
    import ujson as json
except ImportError:
    import json

log = logging.getLogger("hmmm")
log.setLevel(logging.DEBUG)
if not os.path.exists("logs"):
    os.mkdir("logs")

FILENAME = datetime.utcnow().strftime("logs/%Y-%m-%d_%H-%M-%S.log")
logfile = logging.FileHandler(FILENAME, "w", "utf-8")
handler = logging.StreamHandler()
handler.setFormatter(LogFormatter())
logfile.setFormatter(LogFormatter(use_ansi=False))
log.handlers = [logfile, handler]


def get_prefix(bot, message):
    return [f"<@{bot.user.id}> ", bot.config.get("prefix")]

class Hmmm(commands.AutoShardedBot):
    def __init__(self, config: dict):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            description="A bot created for very very weird stuff posted on various subreddits!"  # nopep8
        )
        self.config = config
        self.owners = set(config.get("owners", {}))
        self.uptime = datetime.utcnow()
        self.debug_mode = config.get("debug_mode", True)
        self._zlib = zlib.decompressobj()
        self.socketstats = Counter()
        self.command_usage = Counter()
        self.db = None


    async def is_owner(self, user):
        return user.id in self.owners or await super().is_owner(user)


    async def on_ready(self):
        await self.update()
        log.info(f"{self.user} is ready")
        log.info(f"ID: {self.user.id}")
        log.info(f"Created At: {self.user.created_at}")
        log.info(f"User Count: {len(set(self.get_all_members()))}")
        log.info(f"Channel Count: {len(set(self.get_all_channels()))}")
        log.info(f"Guild Count: {len(self.guilds)}")
        log.info(f"Debug Mode: {self.debug_mode}")


    async def on_socket_raw_receive(self, message):
        data = self._zlib.decompress(message)
        data = json.loads(data)
        if "t" in data:
            self.socketstats[data["t"]] += 1




    async def on_connect(self):
        log.info(f"BOOT @ {FILENAME}")
        log.info("Connecting to discord...")
        self.session = aiohttp.ClientSession(json_serialize=json.dumps)
        try:
            self.db = await asyncpg.create_pool(**self.config["database"])
        except ConnectionRefusedError:
            log.critical("Connecting to database was refused! Killing bot")
            await bot.logout()
            return


        extensions = [x.as_posix().replace("/", ".") for x in pathlib.Path("cogs").iterdir() if x.is_file()]

        extensions.append("jishaku")

        for ext in extensions:
            try:
                self.load_extension(ext.replace(".py", ""))
                log.info(f"Loaded extension: {ext} ")

            except commands.ExtensionAlreadyLoaded:
                log.info(f"Extension was already loaded, reloading ({ext})")
                try:
                    self.reload_extension(ext.replace(".py", ""))
                    log.info(f"Extension reloaded successfully! ({ext})")
                except commands.ExtensionFailed:
                    log.error(f"Extension {ext} failed to load", exc_info=True)
            except commands.ExtensionFailed:
                log.error(f"Extension {ext} failed to load:: ", exc_info=True)

            except commands.ExtensionNotFound:
                log.warning(f"Extension {ext} cannot be found")

            except commands.NoEntryPointError:
                log.warning(f"Extension {ext} has no setup function")

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
            url = f"https://top.gg/api/bots/{self.user.id}/stats"
            async with self.session.post(url, json=payload, headers=headers) as resp:  # nopep8
                data = await resp.json()
                if resp.status == 200:
                    log.info(f"Recieved 200 OK response, {data}")
                else:
                    message = "Recieved {0.method} {0._url} {0.status} {1}"
                    log.warning(message.format(resp, data))

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
    with open("config.json") as f:
        config = json.load(f)
    bot = Hmmm(config=config)
    bot.run(config["bot_token"])
