import asyncio
import math
import sys
import traceback
import logging
import discord
from discord.ext import commands
from discord.ext.commands import Cog

log = logging.getLogger(__name__)





G_MESSAGE = """
COMMAND:    {ctx.command.qualified_name}
AUTHOR:     ID: {ctx.author.id}   NAME: {ctx.author}
CHANNEL:    ID: {ctx.channel.id}   NAME: {ctx.channel}
GUILD:      ID: {ctx.guild.id}   NAME: {ctx.guild}    MEMBER_COUNT: {ctx.guild.member_count} 
INVOCATION: {ctx.message.content}     
"""

DM_MESSAGE = """
COMMAND:    {ctx.command.qualified_name}
AUTHOR:     ID: {ctx.author.id} NAME: {ctx.author}
INVOCATION: {ctx.message.content}     
"""

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.UserInputError)
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

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('**:no_entry: I could not find that member. Please try again.**')

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f"**:no_entry: Oops, I need `{error.missing_perms[0].replace('_', ' ')}` permission to run this command**")

        elif isinstance(error, commands.NotOwner):
            return await ctx.send('**:no_entry: Only my owner can run this command.**')
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"**:no_entry: Woah there, that command is on a cooldown for {math.ceil(error.retry_after)} seconds**")

        elif isinstance(error, commands.NSFWChannelRequired):
            # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.is_nsfw
            return await ctx.send("**:no_entry: This command can only be run in a NSFW channel, as the image could be weird, dark, funny, or __disgusting...__ I can't always stop the bad stuff.**")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send("**:no_entry: You have insufficient permissions to run this command.")

            
        if ctx.guild:
            MESSAGE = G_MESSAGE.format(ctx=ctx)

            
        else:
            MESSAGE = DM_MESSAGE.format(ctx=ctx)

            
        
        log.error(MESSAGE)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
