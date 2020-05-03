from botfuncs.echobot import Echo
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
    self.__handlers = {}
    self.loop.create_task()

  def register(self, t: MessageHandler):
    sc = t.shortcode()
    assert sc not in self.__handlers
    self.__handlers[sc] = t

  async def on_timer(self):
    pass

  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == client.user:
      return
    txt = message.content
    if txt.startswith('!'):
      pos = txt.find(' ')
      moniker = txt[1:] if pos == -1 else txt[1:pos]
      payload = '' if pos == -1 else txt[pos+1:].strip()
      handler = self.__handlers.get(moniker, None)
      if handler:
        await message.channel.send(handler.on_message(payload))
      print('Request from {0.author}: {0.content}'.format(message))


client = RoboClient()

# proceed in a dumb way
client.register(Echo())

with open(os.path.expanduser('~/.robotnik.yml'), 'r') as ymlfile:
  cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
assert 'discord' in cfg
discordsettings = cfg['discord']
assert 'key' in discordsettings
client.run(discordsettings['key'])
