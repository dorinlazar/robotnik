from tools.html import HtmlProcessor
from tools.rss import FeedData
from tools.storage import Storage
import requests
import json
from discord.ext import commands, tasks


class FeedCollection:
    def __init__(self, storage_file: str):
        self.__storage = Storage(storage_file)

    def __restore(self) -> list[FeedData]:
        config = self.__storage.restore()
        return [FeedData(item[0], json.loads(item[1])) for item in config]

    def __store(self, feeds: list[FeedData]) -> None:
        try:
            with gdbm.open(self.__path, "c") as db:
                for f in feeds:
                    db[f.feed] = json.dumps(f.to_json())
        except Exception:
            pass

    def add_feed(self, feed: str) -> str:
        feed_data = FeedData(feed)
        articles = feed_data.update()
        if articles:
            self.__store([feed_data])
            return f"Feed {feed} successfully added, {len(articles)} pre-scanned (and skipped)"
        else:
            return f"Feed {feed} doesn't seem to be ok"

    def update(self) -> list[ArticleInfo]:
        feeds = self.__restore()
        to_store = []
        retval = []
        for f in feeds:
            try:
                articles = f.update()
                if articles:
                    to_store.append(f)
                    retval.extend(articles)
            except Exception as e:
                raise RuntimeError(error=f"Error while retrieving {f.feed}: {str(e)}")
        self.__store(to_store)
        return retval


class RssBot(commands.Cog):
    def __init__(self, bot, storage_file: str):
        self.__feeds = FeedCollection(storage_file)
        self.__bot = bot

    @tasks.loop(seconds=600)
    async def timer_function(self):
        try:
            updates = self.__feeds.update()
            for item in updates:
                message = f"{item.title} {item.link}"
                await self.__bot.get_channel_by_name(name="tweets").send(message[:1900])
        except Exception as e:
            await self.__bot.get_channel_by_name(name="robotest").send(
                f"Am căzut și m-am împiedicat în RSS-uri: {e}"
            )

    def add_site(self, what: str) -> str:
        error = ""
        try:
            if what.startswith("http"):
                what = what[what.find("//") + 2 :]
                if "/" in what:
                    what = what[: what.find("/")]
            r = requests.get(f"https://{what}/")
            tp = TestParser()
            tp.feed(r.text)
            if tp.rss_address:
                address = (
                    tp.rss_address
                    if tp.rss_address.startswith("http")
                    else f"https://{what}{tp.rss_address}"
                )
                return self.add_feed(address)
        except Exception as e:
            error = str(e)
        return f"Unable to parse {what} rss feed: {error}"

    def add_feed(self, what: str) -> str:
        return self.__feeds.add_feed(what)
