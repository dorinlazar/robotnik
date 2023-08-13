import os
import discord
from discord.ext import commands
import yaml
from roboapi import MessageHandler
from botfuncs.twitterbot import TwitterBot
from botfuncs.justwatchbot import JustWatchBot
from botfuncs.ytsearch import YTSearch
from botfuncs.rssbot import RssBot


class RoboClient(commands.Bot):
    def __init__(self, owner=None, guildid=None):
        commands.Bot.__init__(
            self,
            command_prefix="!",
            intents=discord.Intents(messages=True, guilds=True),
        )
        self.__handlers = {}
        self.__owner = owner
        self.__guild_id = discord.Object(id=guildid) if guildid is not None else None
        self.__twitter_cog = None
        self.__rss_cog = None
        print("Owner:", owner)

    async def setup_hook(self):
        if self.__guild_id is not None:
            self.tree.copy_global_to(guild=self.__guild_id)
            await self.tree.sync(guild=self.__guild_id)

    def register(self, t: MessageHandler):
        sc = t.shortcode()
        assert sc not in self.__handlers
        self.__handlers[sc] = t

    def register_tw(self, x):
        self.__twitter_cog = x

    def register_rss(self, x):
        self.__rss_cog = x

    def get_channel_by_name(self, name):
        return next(c for c in self.get_all_channels() if c.name == name)

    async def on_ready(self):
        if self.__twitter_cog:
            await self.add_cog(self.__twitter_cog)
            self.__twitter_cog.timer_function.start()
        if self.__rss_cog:
            await self.add_cog(self.__rss_cog)
            self.__rss_cog.timer_function.start()

        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        if message.author == client.user:
            return
        txt = message.content
        if txt.startswith("!"):
            pos = txt.find(" ")
            moniker = txt[1:] if pos == -1 else txt[1:pos]
            payload = "" if pos == -1 else txt[pos + 1 :].strip()
            handler = self.__handlers.get(moniker, None)
            if handler:
                response = self.__run_command(handler, payload)
                for line in response:
                    await message.channel.send(line)
            elif str(message.author) == self.__owner and txt[1:] == "quit":
                print("Logging out on request")
                await self.close()
                print("Done...")
            print("Request from {0.author}: {0.content}".format(message))

    def __run_command(self, handler, payload):
        try:
            response = handler.on_message(payload).split("\n")
            res = []
            current = ""
            for line in response:
                if len(current) + len(line) + 1 < 2000:
                    if len(current):
                        current = current + "\n"
                    current = current + line
                else:
                    res.append(current)
                    current = line
            if len(current):
                res.append(current)
            return res
        except Exception as e:
            return ["Excepțional!:", str(e)]


if __name__ == "__main__":
    with open(os.path.expanduser("~/.robotnik.yml"), "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    assert "discord" in cfg
    discordsettings = cfg["discord"]
    assert "key" in discordsettings
    assert "twitter" in cfg

    kwargs = {}
    if "client" in cfg:
        kwargs = cfg["client"]
    client = RoboClient(**kwargs)

    @client.tree.command()
    async def echo(interaction: discord.Interaction, what: str):
        await interaction.response.send_message(
            f"Hi, {interaction.user.mention}: {what}"
        )

    justwatch = JustWatchBot()

    @client.tree.command()
    async def movie(interaction: discord.Interaction, what: str, country: str = "RO"):
        response = justwatch.on_country_message(what, country)
        current = ""
        res = []
        for line in response.splitlines():
            if len(current) + len(line) + 1 < 2000:
                if len(current):
                    current = current + "\n"
                current = current + line
            else:
                res.append(current)
                current = line
        if len(current):
            res.append(current)
        if not res:
            res = [f"No response for query: {what}@{country}"]
        for x in res:
            await interaction.response.send_message(x, suppress_embeds=True)

    ytclient = YTSearch()

    @client.tree.command()
    async def yt(interaction: discord.Interaction, what: str):
        await interaction.response.send_message(ytclient.on_message(what))

    rssbot = RssBot(client, os.path.expanduser("~/.robotnik.rss.gdbm"))

    @client.tree.command()
    async def addsite(
        interaction: discord.Interaction, what: str, where: str = "#shorts"
    ):
        await interaction.response.send_message(rssbot.add_site(what, where))

    @client.tree.command()
    async def addfeed(
        interaction: discord.Interaction, what: str, where: str = "#shorts"
    ):
        await interaction.response.send_message(rssbot.add_feed(what, where))

    @client.tree.command()
    async def listfeeds(interaction: discord.Interaction):
        await interaction.response.send_message(rssbot.list_feeds())

    @client.tree.command()
    async def delfeed(interaction: discord.Interaction, what: str):
        await interaction.response.send_message(rssbot.del_feed(what))

    client.register_rss(rssbot)
    # client.register_tw(TwitterBot(bot=client, **cfg["twitter"]))
    client.run(discordsettings["key"])
