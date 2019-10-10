import discord
import aiohttp
import logging
import pathlib
try:
    import ujson as json
except ImportError:
    import json

from discord.ext import commands
from datetime import datetime


log = logging.getLogger(__name__)


class Hmmm(commands.AutoShardedBot):
    def __init__(self, config):
        super().__init__(command_prefix=commands.when_mentioned_or(config.get("prefix", "??")), case_insensitive=True)
        self.remove_command("help")
        self.config = config
        self.owners = set(config.get("owners", {}))
        self.uptime = datetime.utcnow()
        self.debug_mode = config.get("debug_mode", True)


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
        

    
    async def on_connect(self):
        log.info("Connecting to discord...")
        await self.change_presence(status=discord.Status.dnd, activity=discord.Activity(name="myself start", type=discord.ActivityType.watching))
        self.session = aiohttp.ClientSession(json_serialize=json.dumps)

        extensions = [x.as_posix().replace("/", ".") for x in pathlib.Path("hmmm/cogs").iterdir() if x.is_file() and x.name.endswith(".py")]
        extensions.append("jishaku")
        for ext in extensions:
            try:
                self.load_extension(ext.replace(".py", ""))
                log.info(f"Loaded extension: {ext} ")

            except commands.ExtensionAlreadyLoaded:
                log.info(f"Extension was already loaded, reloading ({ext})")
                try:
                    self.reload_extension(ext.replace(".py", ""))
                except commands.ExtensionFailed:
                    log.error(f"Extension {ext} failed to load:: ", exc_info=True)
                
            except commands.ExtensionFailed:
                log.error(f"Extension {ext} failed to load:: ", exc_info=True)
            
            except commands.ExtensionNotFound:
                log.warning(f"Extension {ext} cannot be found")
            
            except commands.NoEntryPointError:
                log.warning(f"Extension {ext} has no setup function")

  

    async def update(self):
        activity = discord.Activity(name=f"??help | {len(self.guilds)} guilds.", type=1, url="https://www.twitch.tv/SpectrixYT")
        await self.change_presence(activity=activity)

        if self.config.get("dbl_token") and not self.debug_mode:
            
            payload = {"server_count" : len(self.guilds)}
            headers = {"Authorization": self.config["dbl_token"] }

            async with self.session.post(f"https://top.gg/api/bots/{self.user.id}/stats", json=payload, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    log.info(f"Recieved 200 OK response, {data}")
                else:
                    log.warning(f"Did not get a OK response: {resp.method} {resp._url} {resp.status} {data}")

    async def logout(self):
        log.debug("logout() got called, logging out and cleaning up tasks")
        try:
            await self.session.close()
        except:
            #TODO: find what exception is raised when the session was already closed
            pass

        return await super().logout()