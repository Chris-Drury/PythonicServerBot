import subprocess
import time

import definitions
import helpers


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
        
async def server_restart(message, server_id):
    await message.channel.send(f'Restarting the {server_id} server...')
    response = await server_down(message, server_id)
    if 'shutdown' in response:
        response = await server_start(message, server_id)
    
    return response

async def server_status(message, server_id):
    await message.channel.send(f'Checking the {server_id} server. Please give me 5 seconds...')

    return helpers.get_server_status(server_id)

async def server_send_cmd(message, server_id, command):
    server_details = helpers.get_server_details(server_id)
    if isinstance(server_details, str): return server_details

    author_roles = message.author.roles
    authorized_roles = server_details['authorized_roles']

    if helpers.validate_roles(author_roles, authorized_roles):
        response_status = helpers.get_server_status(server_id)
        if 'up' in response_status:
            print(command, file=server_details['process'].stdin, flush=True)
            return f'The command {command} was sent. You\'re welcome.' 

        return f'You just wasted my time. {response_status} I\'d very much like you to pay attention next time.'
        
    return f'Sorry, but no. Only {authorized_roles} roles can do this.'

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
    'restart': server_restart,
    'status': server_status,
    'send': server_send_cmd,
    'up': server_start
}
