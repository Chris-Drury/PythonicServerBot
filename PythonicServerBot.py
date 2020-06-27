# PythonicServerBot written by Chris Drury
from discord.ext import commands

import definitions
import helpers
from controls import CONTROL_COMMANDS
from server import SERVER_COMMANDS

bot = commands.Bot(command_prefix=definitions.PREFIX)


@bot.event
async def on_ready():
    print(f'{bot.user.name} is spinning up...')

"""
This will handle all commands given to the PythonicServer Bot.

Args:
    message: The message sent in the bot's Discord server.

For a message to successfully trigger the botit must be predicated by the 
globally determined PREFIX.

A standard message should have the structure 
    PREFIX<command> <server_id> 
Where:
    <command> is a Globally recognised command in either:
        -SERVER_COMMANDS, or
        -CONTROL_COMMANDS
    <server_id> is a server_id corresponding to a server found in SERVER_DETAILS
"""
@bot.event
async def on_message(message):
    if message.content.startswith(definitions.PREFIX):
        response = None
        message.content = message.content[2:]
        split_message = message.content.split()
    else:
        return 

    if len(split_message) > 2:
        await message.channel.send('Wooooow look at you, you can make big commands!')
        response = 'Keep them short.'
    elif len(split_message) > 1:
        if split_message[0] in SERVER_COMMANDS.keys():
            response = await SERVER_COMMANDS[split_message[0]](message, split_message[1])
        else:
            response = 'Why do you torture me like this...' if helpers.validate_roles(message.author.roles, ['Creator']) else 'What the fuck do you want now?'
    elif message.content in CONTROL_COMMANDS.keys():
        response = await CONTROL_COMMANDS[message.content](message)
    else:
        response = 'You don\'t think I can read minds do you? I need a server id.'

    if response:
        await helpers.send_message(message, response)

bot.run(definitions.DISCORD_TOKEN)
