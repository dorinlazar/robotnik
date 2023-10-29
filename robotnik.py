import os
import discord
from discord.ext import commands
import yaml
from botfuncs.ytsearch import YTSearch
from botfuncs.rssbot import RssBot
from botfuncs.tmdb import Tmdb


class RoboClient(commands.Bot):
    def __init__(self, owner=None, guildid=None):
        commands.Bot.__init__(
            self,
            command_prefix="!",
            intents=discord.Intents(messages=True, guilds=True),
        )
        self.__owner = owner
        self.__guild_id = discord.Object(id=guildid) if guildid is not None else None
        self.__rss_cog = None
        print("Owner:", self.__owner)

    async def setup_hook(self):
        if self.__guild_id is not None:
            self.tree.copy_global_to(guild=self.__guild_id)
            await self.tree.sync(guild=self.__guild_id)

    def register_rss(self, x):
        self.__rss_cog = x

    def get_channel_by_name(self, name):
        return next(
            c for c in self.get_all_channels() if c.name == name or str(c.id) == name
        )

    async def on_ready(self):
        if self.__rss_cog:
            await self.add_cog(self.__rss_cog)
            self.__rss_cog.timer_function.start()

        print("Logged on as {0}!".format(self.user))

    # async def on_message(self, message):
    #     if message.author == client.user:
    #         return
    #     txt = message.content
    #     if txt.startswith("!"):
    #         print("Request from {0.author}: {0.content}".format(message))

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


async def send_response(interaction: discord.Interaction, response: list[str]):
    res: list[str] = []
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
    await interaction.response.send_message(res[0], suppress_embeds=True)
    for x in res[1:]:
        await interaction.followup.send(x, suppress_embeds=True)


if __name__ == "__main__":
    with open(os.path.expanduser("~/.robotnik.yml"), "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    assert "discord" in cfg
    discordsettings = cfg["discord"]
    assert "key" in discordsettings

    kwargs = {}
    if "client" in cfg:
        kwargs = cfg["client"]
    client = RoboClient(**kwargs)

    @client.tree.command()
    async def echo(interaction: discord.Interaction, what: str):
        await interaction.response.send_message(
            f"Hi, {interaction.user.mention}: {what}"
        )

    assert "key" in cfg["tmdb"]
    tmdb_client = Tmdb(cfg["tmdb"]["key"])

    @client.tree.command()
    async def movie(
        interaction: discord.Interaction,
        what: str,
        country: str = "RO",
        show_max: int = 3,
    ):
        result = tmdb_client.search_movie(name=what, country=country, show_max=show_max)
        if not result:
            result = [f"No response for query: {what}@{country}"]
        await send_response(interaction, result)

    @client.tree.command()
    async def tv(
        interaction: discord.Interaction,
        what: str,
        country: str = "RO",
        show_max: int = 3,
    ):
        result = tmdb_client.search_tv(name=what, country=country, show_max=show_max)
        if not result:
            result = [f"No response for query: {what}@{country}"]
        await send_response(interaction, result)

    ytclient = YTSearch()

    @client.tree.command()
    async def yt(interaction: discord.Interaction, what: str):
        await interaction.response.send_message(ytclient.on_request(what))

    rssbot = RssBot(client, os.path.expanduser("~/.robotnik.rss.gdbm"))

    @client.tree.command()
    async def addsite(
        interaction: discord.Interaction, what: str, where: str = "<#shorts>"
    ):
        await interaction.response.send_message(rssbot.add_site(what, where))

    @client.tree.command()
    async def addfeed(
        interaction: discord.Interaction, what: str, where: str = "<#shorts>"
    ):
        await interaction.response.send_message(rssbot.add_feed(what, where))

    @client.tree.command()
    async def listfeeds(interaction: discord.Interaction):
        await interaction.response.send_message(rssbot.list_feeds())

    @client.tree.command()
    async def delfeed(interaction: discord.Interaction, what: str):
        await interaction.response.send_message(rssbot.del_feed(what))

    client.register_rss(rssbot)
    client.run(discordsettings["key"])
