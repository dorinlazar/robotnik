import os
import discord
import yaml
from roboapi import MessageHandler

class MessageHub(object):
  def __init__(self):
    self.__handlers = {}

  def load(self, t: MessageHandler):
    sc = t.shortcode()
    assert sc not in self.__handlers
    self.__handlers[sc] = t

class RoboClient(discord.Client):
  def __init__(self):
    discord.Client.__init__(self)
    self.__hub = MessageHub()
    

  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == client.user:
      return

    if message.content.startswith('$hello'):
      await message.channel.send('Hello!')
    print('Message from {0.author}: {0.content}'.format(message))

client = RoboClient()


with open(os.path.expanduser('~/.robotnik.yml'), 'r') as ymlfile:
  cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
assert 'discord' in cfg
discordsettings = cfg['discord']
assert 'key' in discordsettings
client.run(discordsettings['key'])
