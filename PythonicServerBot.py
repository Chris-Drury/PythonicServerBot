# PythonicServerBot written by Chris Drury

import datetime
import os
import random
import subprocess
import sys
import time

from discord.ext import commands

import definitions
import helpers
from controls import CONTROL_COMMANDS

bot = commands.Bot(command_prefix=definitions.PREFIX)

################################################################################
# Server Commands

async def server_down(message, server_id):
    await message.channel.send(f'Shutting down the {server_id} server...')

    server_details = helpers.get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    author_roles = message.author.roles
    authorized_roles = server_details['authorized_roles']

    if helpers.validate_roles(author_roles, authorized_roles):
        response_status = helpers.get_server_status( server_id)
        if 'up' in response_status:
            player_check = await server_players(message, server_id) ## This should be refactored. If a server command should be called, then something should be a helper.

            if definitions.PLAYER_LIST not in player_check:
                print('/stop', file=server_details['process'].stdin, flush=True)
                server_details['process'].terminate()
                return f'Server {server_id} has been shutdown.'
            else:
                response_status = player_check

        return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorized_roles} roles can do this.'

async def server_info(message, server_id):
        server_details = helpers.get_server_details(server_id)  
        if isinstance(server_details, str): return server_details

        info = f''' server {server_id}:
        ```
        {server_details["description"]}
        
        IP: {server_details["host_ip"]}:{server_details["host_port"]}
        Authorized roles: {server_details["authorized_roles"]}
        ```'''

        await message.channel.send(info)

async def server_players(message, server_id):
    response_status = helpers.get_server_status(server_id)
    if 'up' in response_status:
        server_details = helpers.get_server_details(server_id)  
        if isinstance(server_details, str): return server_details

        with open(server_details['cwd'] + server_details['log'], 'r') as file:
            file.read()
            print('/list', file=server_details['process'].stdin, flush=True)
            time.sleep(1)

            players = file.readline().rsplit(':', 1)[-1]

            if players.replace(' \n', ''):
                return f'{definitions.PLAYER_LIST}\n ```{players}```'
            else:
                return 'There are no players connected. *Guess they don\'t like you huh?*'
        
        return 'There was an error reading the logs!'

    else:
        return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'

async def server_status(message, server_id):
    await message.channel.send(f'Checking the {server_id} server. Please give me 5 seconds...')

    return helpers.get_server_status(server_id)

async def server_start(message, server_id):
    await message.channel.send(f'Starting up the {server_id} server. Please give me up to 15 minutes...')

    server_details = helpers.get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    author_roles = message.author.roles
    authorized_roles = server_details['authorized_roles']

    if helpers.validate_roles(author_roles, authorized_roles):
        response_status = helpers.get_server_status(server_id)
        if 'down' in response_status:
            server_details['process'] = subprocess.Popen(["cmd.exe"],  
                                                            creationflags=subprocess.CREATE_NEW_CONSOLE ,
                                                            stdin=subprocess.PIPE,
                                                            cwd=server_details['cwd'],
                                                            text=True)
            print(definitions.SERVER_BATCH, file=server_details['process'].stdin, flush=True)

            t_end = time.time() + 60 * 15
            while time.time() < t_end:
                response_status = helpers.get_server_status(server_id)
                if 'up' in response_status: 
                    return response_status

            return f'There was an issue encountered when starting the {server_id} server... What did you do wrong?'
        
        return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorized_roles} roles can do this.'

SERVER_COMMANDS = {
    'down': server_down,
    'info': server_info,
    'players': server_players,
    'status': server_status,
    'up': server_start
}
################################################################################
# Bot Events
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
