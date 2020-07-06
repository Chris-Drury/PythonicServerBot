import os

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
HELP = '''Here are all of my commands:
```
Server commands:
s!send <server id> <cmd>  Send a custom command straight into the server! 
s!down <server id> ...... Shutdown the server.
                                I'll only shutdown the server if no one is on!
s!info <server id> ...... Get the server's authorised roles, IP, and Port.
                                I'll be cute and give a summary of the server too.
s!players <server id> ... Get the player list of the sever you specified! ...creep.
s!restart <server id> ... Restart the server in one command instead of two!
                                ... Lazy piece of shit.
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
