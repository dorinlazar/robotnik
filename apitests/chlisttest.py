import os
import discord
import yaml


class RoboClient(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        print('Guilds:', self.guilds)

        for guild in self.guilds:
            print('Guild:', guild, guild.channels)
            for channel in guild.channels:
                print('  - ', channel)
                if channel.name == 'robotest':
                    await channel.send('Spamming some message, for test purposes')
        await self.logout()


client = RoboClient()

with open(os.path.expanduser('~/.robotnik.yml'), 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
assert 'discord' in cfg
discordsettings = cfg['discord']
assert 'key' in discordsettings
client.run(discordsettings['key'])
