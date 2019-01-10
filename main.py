import discord, asyncio, time, datetime, random, json, aiohttp, logging, os
from discord.ext import commands
from time import ctime
from os import listdir
from os.path import isfile, join

with open("databases/thesacredtexts.json") as f:
    config = json.load(f)

class hmmm(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("??"),
                         owner_id=276707898091110400,
                         case_insensitive=True)

    async def update_activity(self):
        await self.change_presence(
            activity=discord.Activity(
                name=f"??help | {len(self.guilds)} guilds.",
                type=1,
                url="https://www.twitch.tv/SpectrixYT"))
        print("Updated presence")
        payload = {"server_count"  : len(self.guilds)}
        url = "https://discordbots.org/api/bots/320590882187247617/stats"
        headers = {"Authorization" : config["tokens"]["dbltoken"]}
        async with aiohttp.ClientSession() as aioclient:
                await aioclient.post(
                    url,
                    data=payload,
                    headers=headers)
        print(f"Posted payload to Discord Bot List:\n{payload}")

    async def on_ready(self):
        print("=======================\nConnected\n=========")
        await self.update_activity()

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_guild_join(self, guild):
        await self.update_activity()
        try:
            embed = discord.Embed(color=discord.Color(value=0x36393e))
            embed.set_author(name="Confused? You should be, this bot makes no sense. Take this, it might help:")
            embed.add_field(name="Prefix", value="`??`, or **mention me.**")
            embed.add_field(name="Command help", value="??help")
            embed.add_field(name="Support Server", value="[Join, it's fun here](https://discord.gg/Kghqehz)")
            embed.add_field(name="Upvote", value="[Click here](https://discordbots.org/bot/320590882187247617/vote)")
            embed.set_thumbnail(url="https://styles.redditmedia.com/t5_2qq6z/styles/communityIcon_ybmhghdu9nj01.png")
            embed.set_footer(text=f"Thanks to you, this monstrosity of a bot is now on {len(self.guilds)} servers!", icon_url="https://media.giphy.com/media/ruw1bRYN0IXNS/giphy.gif")
            await guild.system_channel.send(content="**Hello World! Thanks for inviting me! :wave: **", embed=embed)
        except:
            pass

    async def on_guild_remove(self):
        await self.update_activity()

    def initiate_start(self):
        self.remove_command("help")
        lst = [f for f in listdir("cogs/") if isfile(join("cogs/", f))]
        no_py = [s.replace('.py', '') for s in lst]
        startup_extensions = ["cogs." + no_py for no_py in no_py]
        try:
            for cogs in startup_extensions:
                self.load_extension(cogs)
                print(f"Loaded {cogs}")
            print("\nAll Cogs Loaded\n===============\nLogging into Discord...")
            super().run(config['tokens']['token'])
        except Exception as e:
            print(f"\n###################\nPOSSIBLE FATAL ERROR:\n{e}\n\n\
                    THIS MEANS THE BOT HAS NOT STARTED CORRECTLY!")

if __name__ == '__main__':
    hmmm().initiate_start()