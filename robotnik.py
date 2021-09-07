import os
import discord
import yaml
import asyncio
from roboapi import MessageHandler
from botfuncs.echobot import Echo
from botfuncs.twitterbot import TwitterBot
from botfuncs.justwatchbot import JustWatchBot


class MessageHub(object):
  def __init__(self):
    self.__handlers = {}

  def load(self, t: MessageHandler):
    sc = t.shortcode()
    assert sc not in self.__handlers
    self.__handlers[sc] = t


class RoboClient(discord.Client):
  def __init__(self, owner=None):
    discord.Client.__init__(self)
    self.__handlers = {}
    self.__timer_functions = []
    self.__owner = owner
    print('Owner:', owner)

  def register(self, t: MessageHandler):
    sc = t.shortcode()
    assert sc not in self.__handlers
    self.__handlers[sc] = t

  def register_timer(self, function):
    self.__timer_functions.append(function)

  async def on_timer(self):
    while True:
      await asyncio.sleep(1)
      stuff_to_send = []
      for f in self.__timer_functions:
        stuff_to_send.extend(f())
      for msg in stuff_to_send:
        await self.get_channel_by_name(msg[0]).send(msg[1])

  def get_channel_by_name(self, name):
    return next(c for c in self.get_all_channels() if c.name == name)

  async def on_ready(self):
    self.loop.create_task(self.on_timer())
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
      elif str(message.author) == self.__owner and txt[1:] == 'quit':
        print('Logging out on request')
        await self.logout()
        print('Done...')
      print('Request from {0.author}: {0.content}'.format(message))


with open(os.path.expanduser('~/.robotnik.yml'), 'r') as ymlfile:
  cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
assert 'discord' in cfg
discordsettings = cfg['discord']
assert 'key' in discordsettings
assert 'twitter' in cfg

kwargs = {}
if 'client' in cfg:
  kwargs = cfg['client']
client = RoboClient(**kwargs)
client.register(Echo())
client.register(JustWatchBot())

x = TwitterBot(**cfg['twitter'])
client.register_timer(x.on_timer)
client.run(discordsettings['key'])
