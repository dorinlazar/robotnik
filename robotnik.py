import os
import discord
import yaml
import asyncio
from roboapi import MessageHandler
from botfuncs.echobot import Echo
from botfuncs.twitterbot import TwitterBot
from botfuncs.justwatchbot import JustWatchBot
from botfuncs.ytsearch import YTSearch


class RoboClient(discord.Client):
  def __init__(self, owner=None, guildid=None):
    discord.Client.__init__(self, intents=discord.Intents(messages=True, guilds=True))
    self.__handlers = {}
    self.__timer_functions = []
    self.__owner = owner
    self.__guild_id = discord.Object(id=guildid) if guildid is not None else None
    self.tree = discord.app_commands.CommandTree(self)
    print('Owner:', owner)

  async def setup_hook(self):
    if (self.__guild_id is not None):
      self.tree.copy_global_to(guild=self.__guild_id)
      await self.tree.sync(guild=self.__guild_id)

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
        await self.get_channel_by_name(msg[0]).send(msg[1][:1900])

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
        response = self.__run_command(handler, payload)
        for line in response:
          await message.channel.send(line)
      elif str(message.author) == self.__owner and txt[1:] == 'quit':
        print('Logging out on request')
        await self.close()
        print('Done...')
      print('Request from {0.author}: {0.content}'.format(message))

  def __run_command(self, handler, payload):
    try:
      response = handler.on_message(payload).split('\n')
      res = []
      current = ''
      for line in response:
        if len(current) + len(line) + 1 < 2000:
          if len(current):
            current = current + '\n'
          current = current + line
        else:
          res.append(current)
          current = ''
      if len(current):
        res.append(current)
      return res
    except Exception as e:
      return ['Excepțional!:', str(e)]


if __name__ == '__main__':
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

  # client.register(Echo())
  @client.tree.command()
  async def echo(interaction: discord.Interaction, what: str):
    await interaction.response.send_message(f'Hi, {interaction.user.mention}: {what}')

  # client.register(JustWatchBot())
  justwatch = JustWatchBot()

  @client.tree.command()
  async def movie(interaction: discord.Interaction, what: str):
    await interaction.response.send_message(justwatch.on_message(what))

  # client.register(YTSearch())
  ytclient = YTSearch()

  @client.tree.command()
  async def yt(interaction: discord.Interaction, what: str):
    await interaction.response.send_message(ytclient.on_message(what))

  x = TwitterBot(**cfg['twitter'])
  client.register_timer(x.on_timer)
  client.run(discordsettings['key'])
