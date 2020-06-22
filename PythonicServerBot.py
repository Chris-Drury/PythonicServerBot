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
    *Server commands*:
    s!down <Server id> ......X.. Shutdown matching server.
                                    I'll only shutdown the server if no one is on!
    s!up <Server id> ........... Startup matching server.

    *Server statuses*:
    s!players <server id> ...X.. Get the player list of the sever you specified! ...Fucking creep.
    s!status ................X.. Get the status of every known server
    s!status <Server id> ....... Get the status of the server you specified!
                                    I'll check for 5seconds before I make my decision.

    *My own commands*:
    s!fuckoff .................. Shut me down, daddy.
    s!help ..................... Ask me for help... you dumbass

    The *server ids* I know are:
    FTB ........................ Chris' FTB Minecraft Server
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


def details(server_id):
    if server_id in SERVER_IDS.keys():
        return SERVER_IDS[server_id]
    else:
        return 'I don\'t think you read the ids I know. Try again.'

def check_roles(author_roles, authorised_roles):
    for role in author_roles:
        if role.name in authorised_roles:
            return True

    return False

def status(server_id):
    server_details = details(server_id)
    if isinstance(server_details, str): return server_details

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        if sock.connect_ex((server_details['host_ip'], server_details['host_port'])) == 0:
            return f'The {server_id} server is up.'
        else:
            return f'The {server_id} server is down.'

def up(author_roles, server_id):
    server_details = details(server_id)
    if isinstance(server_details, str): return server_details
    authorised_roles = server_details['authorised_roles']

    if check_roles(author_roles, authorised_roles):
        response_status = status(server_id)
        if 'down' in response_status:
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
                response_status = status(server_id)
                if 'up' in response_status: 
                    print('/list', file=server_details['process'].stdin, flush=True)
                    return response_status

            return f'There was an issue encountered when starting the {server_id} server... What did you do wrong?'
        else:
            return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorised_roles} roles can do this.'

def down(author_roles, server_id):
    server_details = details(server_id)
    if isinstance(server_details, str): return server_details
    authorised_roles = server_details['authorised_roles']

    if check_roles(author_roles, authorised_roles):
        response_status = status(server_id)
        if 'up' in response_status:
            return 'This is yet to be implemented!'
        else:
            return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorised_roles} roles can do this.'

@bot.event
async def on_ready():
    print(f'{bot.user.name} is spinning up...')

@bot.event
async def on_message(message):
    if not message.content.startswith(PREFIX):
        return

    response = None
    split_message = message.content.split()

    if len(split_message) > 1:
        command = split_message[0]
        server_id = split_message[1]

        if 'status' in command:
            await message.channel.send(f'Checking the {server_id} server. Please give me 5 seconds...')
            response = status(server_id)
        elif 'up' in command:
            await message.channel.send(f'Starting up the {server_id} server. Please give me up to 15 minutes...')
            response = up(message.author.roles, server_id)
        elif 'down' in command:
            await message.channel.send(f'Shutting down the {server_id} server...')
            response = down(message.author.roles, server_id)
        elif 'players' in command:
            response = 'This is yet to be implemented!'
        else:
            response = 'Why do you torture me like this...' if check_roles(message.author.roles, ['Creator']) else 'What the fuck do you want now?'

    elif 's!fuckoff' in split_message:
        if check_roles(message.author.roles, ['Creator']):
            await message.channel.send('UGH FINE')
            print("Shutting down...")
            await bot.close()
            raise Exception(f'I was shutdown by {message.author.name}')
        else:
            response = 'Fuck you too, asshole'

    elif 's!help' in split_message:
        await message.channel.send('I HAVE BEEN BECKONED!!')
        response = HELP

    elif 's!status' in split_message:
        response = 'This is yet to be implemented!'

    else:
        response = 'You don\'t think I can read minds do you? I need a server id.'

    if response:
        await message.channel.send(response)

bot.run(DISCORD_TOKEN)
