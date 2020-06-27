import helpers
from definitions import HELP, SERVER_IDS

async def shut_down(message):
    if helpers.validate_roles(message.author.roles, ['Creator']):
        await message.channel.send('UGH FINE. I should warn you though, this isn\'t complete yet. You could orphan a server!')
        return 'HAHA NOPE. This is under construction'
        # await bot.close()
        # raise Exception(f'I was shutdown by {message.author.name}')
    else:
        return 'Fuck you too, asshole'

async def get_help(message):
        await message.channel.send('I HAVE BEEN BECKONED!!\n')
        return HELP

async def all_statuses(message):
    await message.channel.send(f'Checking all server statuses. Please give me {len(SERVER_IDS.keys()) * 5} seconds...')

    response = 'Here are the current server statuses:\n ```'
    for server_id in SERVER_IDS.keys():
        response += '\n' + helpers.get_server_status(server_id)

    return response + '```\nAre you happy now? I\'d very much like you to leave me alone now.'

CONTROL_COMMANDS = {
    'fuckoff': shut_down,
    'help': get_help,
    'status': all_statuses
}
