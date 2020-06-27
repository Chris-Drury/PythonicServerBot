import socket

from definitions import SERVER_IDS


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
