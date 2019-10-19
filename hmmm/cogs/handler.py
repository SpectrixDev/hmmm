import asyncio
import math
import sys
import traceback
import logging
import discord
from discord import utils
from discord.ext import commands
from discord.ext.commands import Cog

log = logging.getLogger(__name__)





GUILD_MESSAGE = """
COMMAND:    {ctx.command}
AUTHOR:     ID: {ctx.author.id}   NAME: {ctx.author}
CHANNEL:    ID: {ctx.channel.id}   NAME: {ctx.channel}
GUILD:      ID: {ctx.guild.id}   NAME: {ctx.guild}    MEMBER_COUNT: {ctx.guild.member_count} 
INVOCATION: {ctx.message.content}     
ERROR:
{error}
"""

DM_MESSAGE = """
COMMAND:    {ctx.command}
AUTHOR:     ID: {ctx.author.id} NAME: {ctx.author}
INVOCATION: {ctx.message.clean_content}     

ERROR: 
{error}
"""

COMMAND_MESSAGE = """
COMMAND:    {ctx.command}
AUTHOR:     ID: {ctx.author.id} NAME: {ctx.author}
INVOCATION: {ctx.message.clean_content}     
"""


GUILD_COMMAND_MESSAGE = """
COMMAND:    {ctx.command}
AUTHOR:     ID: {ctx.author.id}   NAME: {ctx.author}
CHANNEL:    ID: {ctx.channel.id}   NAME: {ctx.channel}
GUILD:      ID: {ctx.guild.id}   NAME: {ctx.guild}    MEMBER_COUNT: {ctx.guild.member_count} 
INVOCATION: {ctx.message.clean_content}     
"""


GUILD_T_MESSAGE = """
{5} guild 
GUILD: NAME {0}       ID: {0.id}
OWNER: NAME {0.owner} ID: {0.owner.id}
MEMBER COUNT: ALL {1} BOTS: {3} HUMANS: {4}
CREATED_AT: {0.created_at}
"""

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook = discord.AsyncWebhookAdapter(self.bot.session)
    


    async def webhook_log(self, message):
        if self.bot.config.get("webhook_url"):
            await self.webhook.request("POST", self.bot.config.get("webhook_url"), {"content" : message})
            
        
    
    @Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.update()

        BOTS = sum(1 for x in guild.members if x.bot)
        HUMANS = sum(1 for x in guild.members if not x.bot)
        ALL = guild.member_count

        payload = {
            "content" : "```fix\n" + GUILD_T_MESSAGE.format(guild, ALL, BOTS, HUMANS, 'Joined') + "\n```"
        }
        await self.webhook_log(payload)
        
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(color=discord.Color(value=0x36393e))
            embed.set_author(name="Confused? You should be, this bot makes no sense. Take this, it might help:")
            embed.add_field(name="Prefix", value=f"`{self.bot.config.get('prefix')}`, or **mention me.**")
            embed.add_field(name="Command help", value=f"{self.bot.config.get('prefix')}help")
            embed.add_field(name="Support Server", value="[Join, it's fun here](https://discord.gg/Kghqehz)")
            embed.add_field(name="Upvote", value=f"[Click here](https://discordbots.org/bot/{self.bot.user.id}/vote)")
            embed.set_thumbnail(url=str(self.bot.user.avatar_url))
            embed.set_footer(text=f"Thanks to you, this monstrosity of a bot is now on {len(self.bot.guilds):,d} servers!", icon_url="https://media.giphy.com/media/ruw1bRYN0IXNS/giphy.gif")
            await guild.system_channel.send(content="**Hello gamers! Thanks for inviting me! :wave: **", embed=embed)

    @Cog.listener()
    async def on_guild_remove(self, guild):
        
        BOTS = sum(1 for x in guild.members if x.bot)
        HUMANS = sum(1 for x in guild.members if not x.bot)
        ALL = guild.member_count

        payload = {
            "content" : "```fix\n" + GUILD_T_MESSAGE.format(guild, ALL, BOTS, HUMANS, 'Lefted') + "\n```"
        } 
        await self.webhook_log(payload)
        await self.bot.update()

    @Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.guild:
            MESSAGE = GUILD_COMMAND_MESSAGE.format(ctx=ctx)
        else:
            MESSAGE = COMMAND_MESSAGE.format(ctx=ctx)
        
        log.info(MESSAGE)
        

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        
        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, "original", error)

        ignored = (
            commands.UserInputError,
            commands.CommandNotFound
        )
        
        if isinstance(error, ignored): 
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f'**:no_entry: `{ctx.command}` can not be used in Private Messages.**')
            except:
                pass

        elif isinstance(error, commands.NSFWChannelRequired):
            # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.is_nsfw
            return await ctx.send("**:no_entry: This post can only be seen in a NSFW channel, as the image could be weird, dark, funny, or __disgusting...__ I can't always stop the bad stuff.**")

            

        if ctx.guild:
            payload = GUILD_MESSAGE.format(ctx=ctx, error=error)            
            
        else:
            payload = DM_MESSAGE.format(ctx=ctx, error=error) 
            

        
        await self.webhook_log(payload)
        log.error(payload)
        await ctx.send("Seems like an unhandled error has occured, my developers has been notified!")

def setup(bot):
    bot.add_cog(EventHandler(bot))
