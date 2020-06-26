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
s!down <server id> ...... Shutdown the server.
                                I'll only shutdown the server if no one is on!
s!info <server id> ...... Get the server's authorised roles, IP, and Port.
                                I'll be cute and give a summary of the server too.
s!players <server id> ... Get the player list of the sever you specified! ...creep.
s!status <server id> .... Get the status of the server you specified!
                                I'll check for 5 seconds before I make my decision.
s!up <server id> ........ Startup the server.

Controls:
s!fuckoff ............... Shut me down, daddy.
s!help .................. Ask me for help ... you dumbass.
s!status ................ Get the status of every known server.

The server ids I know are:
FTB ...... Chris' FTB Minecraft Server.
JMC ...... Chris' Java 1.16 Server.

```
'''
PLAYER_LIST = 'Player list:'
PREFIX= 's!'
SERVER_BATCH = 'start.bat'
SERVER_IDS={
    'FTB': {
        'authorized_roles': ['Minecraft', 'Creator'],
        'cwd': 'C:\\Users\\User\\Documents\\MC Server\\FTB',
        'description': "A server for FTB Ultimate Reloaded v1.9.0 on Minecraft v1.12.2.",
        'host_ip': os.environ['LOCAL_SERVER_IP'], 
        'host_port': 25565,
        'process': None,
        'log': '\\logs\\latest.log'
    },
    'JMC': {
        'authorized_roles': ['Minecraft', 'Creator'],
        'cwd': 'C:\\Users\\User\\Documents\\MC Server\\JMC',
        'description': "A server for Minecraft Java Edition: Nether Update",
        'host_ip': os.environ['LOCAL_SERVER_IP'], 
        'host_port': 25566,
        'process': None,
        'log': '\\logs\\latest.log'
    }
}

bot = commands.Bot(command_prefix=PREFIX)
################################################################################
# Helpers

# Append custom messages to all sent messages
async def send_message(message, response):
    addition = ''
    await message.channel.send(response + addition)

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
            return f'The {server_id} server is up @ {server_details["host_ip"]}:{server_details["host_port"]}.'
        else:
            return f'The {server_id} server is down.'

# Validate the author's roles against an authorised role list
def validate_roles(author_roles, authorized_roles):
    for role in author_roles:
        if role.name in authorized_roles:
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
    authorized_roles = server_details['authorized_roles']

    if validate_roles(author_roles, authorized_roles):
        response_status = get_server_status( server_id)
        if 'up' in response_status:
            player_check = await server_players(message, server_id) ## This should be refactored. If a server command should be called, then something should be a helper.

            if PLAYER_LIST not in player_check:
                print('/stop', file=server_details['process'].stdin, flush=True)
                server_details['process'].terminate()
                return f'Server {server_id} has been shutdown.'
            else:
                response_status = player_check

        return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorized_roles} roles can do this.'

async def server_info(message, server_id):
        server_details = get_server_details(server_id)  
        if isinstance(server_details, str): return server_details

        info = f''' server {server_id}:
        ```
        {server_details["description"]}
        
        IP: {server_details["host_ip"]}:{server_details["host_port"]}
        Authorized roles: {server_details["authorized_roles"]}
        ```'''

        await message.channel.send(info)

async def server_players(message, server_id):
    response_status = get_server_status(server_id)
    if 'up' in response_status:
        server_details = get_server_details(server_id)  
        if isinstance(server_details, str): return server_details

        with open(server_details['cwd'] + server_details['log'], 'r') as file:
            file.read()
            print('/list', file=server_details['process'].stdin, flush=True)
            time.sleep(1)

            players = file.readline().rsplit(':', 1)[-1]

            if players.replace(' \n', ''):
                return f'{PLAYER_LIST}\n ```{players}```'
            else:
                return 'There are no players connected. *Guess they don\'t like you huh?*'
        
        return 'There was an error reading the logs!'

    else:
        return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'

async def server_status(message, server_id):
    await message.channel.send(f'Checking the {server_id} server. Please give me 5 seconds...')

    return get_server_status(server_id)

async def server_start(message, server_id):
    await message.channel.send(f'Starting up the {server_id} server. Please give me up to 15 minutes...')

    server_details = get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    author_roles = message.author.roles
    authorized_roles = server_details['authorized_roles']

    if validate_roles(author_roles, authorized_roles):
        response_status = get_server_status(server_id)
        if 'down' in response_status:
            server_details['process'] = subprocess.Popen(["cmd.exe"],  
                                                            creationflags=subprocess.CREATE_NEW_CONSOLE ,
                                                            stdin=subprocess.PIPE,
                                                            cwd=server_details['cwd'],
                                                            text=True)
            print(SERVER_BATCH, file=server_details['process'].stdin, flush=True)

            t_end = time.time() + 60 * 15
            while time.time() < t_end:
                response_status = get_server_status(server_id)
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
