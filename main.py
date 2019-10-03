import discord
import aiohttp
import contextlib
import logging

try:
    # a json implementation for python written in C, provides the
    # same API
    import ujson as json
except ImportError:
    import json

with open("databases/thesacredtexts.json") as f:
    config = json.load(f)

from datetime import datetime
from discord.ext import commands 


# let's make the stdout look pretty for logging :D

class ANSIFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt="[{asctime} {name}/{levelname}]: {message}", datefmt=r"%Y/%m/%d %H:%M:%S", style="{")
        self.codes = {
            "WARN"    : "\33[33m",
            "CRITICAL": "\33[95m",
            "ERROR"   : "\33[31m",
            "DEBUG"    : "\33[32;1m",
            "RESET"   : "\33[0m"       
        }
    
    def format(self, r):
        if r.levelname == "WARNING":
            r.levelname = "WARN"
        message = super().format(r)
        if not r.levelname in self.codes:
            return message
        
        return self.codes[r.levelname.upper()] + message + self.codes["RESET"]



handler = logging.StreamHandler()
handler.setFormatter(ANSIFormatter())

log = logging.getLogger("hmmm")
log.setLevel(logging.DEBUG)
log.addHandler(handler)



class hmmm(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("??"),
                         owner_id=276707898091110400,
                         case_insensitive=True)

        with contextlib.suppress(DeprecationWarning):          
            self.session = aiohttp.ClientSession(json_serialize=json.dumps)
        
        self.uptime = datetime.utcnow()

    async def update_activity(self):
        await self.change_presence(
            activity=discord.Activity(
                name=f"??help | {len(self.guilds)} guilds.",
                type=1,
                url="https://www.twitch.tv/SpectrixYT"))
        payload = {"server_count"  : len(self.guilds)}
        url = "https://top.gg/api/bots/320590882187247617/stats"
        headers = {"Authorization" : config["tokens"]["dbltoken"]}
        async with self.session.post(url, json=payload, headers=headers)
        print(f"Posted payload to Discord Bot List:\n{payload}")

    async def on_ready(self):
        log.info(f"{self.user} is ready")
        log.info(f"")
        log.info(f"Guild Count: {len(self.guilds)}")



    async def on_guild_join(self, guild):
        await self.update_activity()

        if guild.system_channel:
            embed = discord.Embed(color=discord.Color(value=0x36393e))
            embed.set_author(name="Confused? You should be, this bot makes no sense. Take this, it might help:")
            embed.add_field(name="Prefix", value="`??`, or **mention me.**")
            embed.add_field(name="Command help", value="??help")
            embed.add_field(name="Support Server", value="[Join, it's fun here](https://discord.gg/Kghqehz)")
            embed.add_field(name="Upvote", value="[Click here](https://discordbots.org/bot/320590882187247617/vote)")
            embed.set_thumbnail(url="https://styles.redditmedia.com/t5_2qq6z/styles/communityIcon_ybmhghdu9nj01.png")
            embed.set_footer(text=f"Thanks to you, this monstrosity of a bot is now on {len(self.guilds)} servers!", icon_url="https://media.giphy.com/media/ruw1bRYN0IXNS/giphy.gif")
            await guild.system_channel.send(content="**Hello World! Thanks for inviting me! :wave: **", embed=embed)

    async def on_guild_remove(self):
        await self.update_activity()

    def run(self):
        self.remove_command("help")

        extensions = [x.as_posix().replace("/", ".") for x in pathlib.Path("cogs").iterdir() if x.is_file() and x.name.endswith(".py")]

        try:
            for ext in extensions:
                try:
                    self.load_extension(ext.replace(".py", ""))
                    log.info(f"Loaded extension:: {ext} ")
            
                except commands.Exte

                
            
            super().run(config['tokens']['token'])
        except Exception:
            log.error("Error while trying to start bot::", exc_info=True)

if __name__ == '__main__':
    bot = hmmm()
    bot.run()