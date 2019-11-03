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


GUILD_STATUS_MESSAGE = """
{0} guild
GUILD: NAME {1}       ID: {1.id}
OWNER: NAME {1.owner} ID: {1.owner.id}
MEMBER COUNT: ALL:{2} BOTS:{3} HUMANS:{4}
CREATED_AT: {1.created_at}
"""