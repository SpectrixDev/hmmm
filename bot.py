import logging
import hmmm


handler = logging.StreamHandler()
handler.setFormatter(ANSIFormatter())

    with open("config.json") as f:
        config = json.load(f)
    bot = hmmm(config=config)
    @bot.event
    async def on_message_edit(before, after):
        if await bot.is_owner(after.author):
            await bot.process_commands(after)

            
    bot.run()
