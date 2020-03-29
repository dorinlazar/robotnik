import os
import discord
import yaml

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == client.user:
      return

    if message.content.startswith('$hello'):
      await message.channel.send('Hello!')
    print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()


with open(os.path.expanduser('~/.robotnik.yml'), 'r') as ymlfile:
  cfg = yaml.load(ymlfile)
client.run()
