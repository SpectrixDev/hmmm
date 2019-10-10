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

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook = discord.AsyncWebhookAdapter(self.bot.session)
    
    @Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.update()
        
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
        
        ignored = (commands.UserInputError, commands.CommandNotFound)
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored): 
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'**:no_entry: `{ctx.command}` has been disabled.**')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'**:no_entry: `{ctx.command}` can not be used in Private Messages.**')
            except:
                pass

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f"**:no_entry: Oops, I need `{error.missing_perms[0].replace('_', ' ')}` permission to run this command**")

        elif isinstance(error, commands.NotOwner):
            return await ctx.send('**:no_entry: Only my owner can run this command.**')
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"**:no_entry: Woah there, that command is on a cooldown for {math.ceil(error.retry_after)} seconds**")

        elif isinstance(error, commands.NSFWChannelRequired):
            # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.is_nsfw
            return await ctx.send("**:no_entry: This command can only be used in a NSFW channel, as the image could be weird, dark, funny, or __disgusting...__ I can't always stop the bad stuff.**")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("**:no_entry: You have insufficient permissions to run this command.")

            
        payload = {}

        if ctx.guild:
            MESSAGE = GUILD_MESSAGE.format(ctx=ctx, error=error)
            payload["content"] =  f"```md\n{GUILD_MESSAGE.format(ctx=ctx, error=error)}\n```"
            
            
        else:
            MESSAGE = DM_MESSAGE.format(ctx=ctx, error=error)
            payload["content"] =  f"```md\n{DM_MESSAGE.format(ctx=ctx, error=error)}\n```"
            

        
        if self.bot.config.get("webhook_url"):
            
            await self.webhook.request("POST", self.bot.config.get("webhook_url"), payload)
            log.error(MESSAGE)
            await ctx.send("Seems like an unhandled error has occured, my creator has been notified!")

def setup(bot):
    bot.add_cog(EventHandler(bot))
