# PythonicServerBot written by Chris Drury

import os
import random
import socket
import subprocess
import sys
import time
import datetime

from discord.ext import commands

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
HELP = '''Here are all of my commands:
```
Server commands:
s!down <Server id> .    . Shutdown matching server.
                                I'll only shutdown the server if no one is on!
s!up <Server id> ........ Startup matching server.

Server statuses:
s!players <server id> . . Get the player list of the sever you specified! ...Fucking creep.
s!status ................ Get the status of every known server
s!status <Server id> .... Get the status of the server you specified!
                                I'll check for 5 seconds before I make my decision.

Controls:
s!fuckoff ............... Shut me down, daddy.
s!help .................. Ask me for help... you dumbass

The server ids I know are:
FTB ...... Chris' FTB Minecraft Server
```
'''
PREFIX= 's!'
SERVER_BATCH = 'start.bat'
SERVER_IDS={
    'FTB': {
        'authorised_roles': ['Minecraft', 'Creator'],
        'cwd': 'C:\\Users\\User\\Documents\\MC Server',
        'host_ip': os.environ['FTB_SERVER_IP'], 
        'host_port': 25565,
        'process': None,
        'log': None
    }
}

bot = commands.Bot(command_prefix=PREFIX)
################################################################################
# Helpers

# Append custom messages to all sent messages
async def send_message(message, response):
    await message.channel.send(response + '\nOH! And daddy is going to work on my s!players command next!!')

# Get details for a specified server
def get_server_details(server_id):
    if server_id in SERVER_IDS.keys():
        return SERVER_IDS[server_id]
    else:
        return 'I don\'t think you read the ids I know. Try again.'

def get_server_status(server_id):
    server_details = get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        if sock.connect_ex((server_details['host_ip'], server_details['host_port'])) == 0:
            return f'The {server_id} server is up.'
        else:
            return f'The {server_id} server is down.'

# Validate the author's roles against an authorised role list
def validate_roles(author_roles, authorised_roles):
    for role in author_roles:
        if role.name in authorised_roles:
            return True

    return False

################################################################################
# Control Commands

async def shut_down(message):
    if validate_roles(message.author.roles, ['Creator']):
        await message.channel.send('UGH FINE. I should warn you though, this isn\'t complete yet. You could orphan a server!')
        await bot.close()
        raise Exception(f'I was shutdown by {message.author.name}')
    else:
        return 'Fuck you too, asshole'

async def get_help(message):
        await message.channel.send('I HAVE BEEN BECKONED!!\n')
        return HELP

async def all_statuses(message):
    await message.channel.send(f'Checking all server statuses. Please give me {len(SERVER_IDS.keys()) * 5} seconds...')

    response = 'Here are the current server statuses:\n ```'
    for server_id in SERVER_IDS.keys():
        response += '\n' + get_server_status(server_id)

    return response + '```\nAre you happy now? I\'d very much like you to leave me alone now.'

CONTROL_COMMANDS = {
    'fuckoff': shut_down,
    'help': get_help,
    'status': all_statuses
}
################################################################################
# Server Commands

async def server_down(message, server_id):
    await message.channel.send(f'Shutting down the {server_id} server...')

    server_details = get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    author_roles = message.author.roles
    authorised_roles = server_details['authorised_roles']

    if validate_roles(author_roles, authorised_roles):
        response_status = await server_status(message, server_id)
        if 'up' in response_status:
            return 'This is yet to be implemented!'
        else:
            return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorised_roles} roles can do this.'

async def server_players(message, server_id):
    await message.channel.send(f'Checking the current players on the {server_id} server...')

    return 'This is yet to be implemented!'

async def server_status(message, server_id):
    await message.channel.send(f'Checking the {server_id} server. Please give me 5 seconds...')

    return get_server_status(server_id)

async def server_start(message, server_id):
    await message.channel.send(f'Starting up the {server_id} server. Please give me up to 15 minutes...')

    server_details = get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    author_roles = message.author.roles
    authorised_roles = server_details['authorised_roles']

    if validate_roles(author_roles, authorised_roles):
        if 'down' in get_server_status(server_id):
            server_details['log'] = open(f'{server_id}/Log_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.txt', 'w+')
            server_details['process'] = subprocess.Popen(["cmd.exe"],  
                                                            creationflags=subprocess.CREATE_NEW_CONSOLE ,
                                                            stdin=subprocess.PIPE, 
                                                            stdout=server_details['log'],
                                                            cwd=server_details['cwd'],
                                                            text=True)
            print(SERVER_BATCH, file=server_details['process'].stdin, flush=True)

            t_end = time.time() + 60 * 15
            while time.time() < t_end:
                response_status = get_server_status(server_id)
                if 'up' in response_status: 
                    print('/list', file=server_details['process'].stdin, flush=True)
                    return response_status

            return f'There was an issue encountered when starting the {server_id} server... What did you do wrong?'
        else:
            return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorised_roles} roles can do this.'

SERVER_COMMANDS = {
    'down': server_down,
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
    if message.content.startswith(PREFIX):
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
            response = 'Why do you torture me like this...' if validate_roles(message.author.roles, ['Creator']) else 'What the fuck do you want now?'
    elif message.content in CONTROL_COMMANDS.keys():
        response = await CONTROL_COMMANDS[message.content](message)
    else:
        response = 'You don\'t think I can read minds do you? I need a server id.'

    if response:
        await send_message(message, response)

bot.run(DISCORD_TOKEN)
