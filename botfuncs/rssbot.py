from tools.html import HtmlProcessor
from tools.rss import FeedData, ArticleInfo
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
        self.__storage.store_all([(f.feed, f.to_json()) for f in feeds])

    def add_feed(self, feed: str) -> str:
        feed_data = FeedData(feed)
        articles = feed_data.get_new_articles()
        if articles:
            self.__store([feed_data])
            return f"Feed {feed} successfully added, {len(articles)} pre-scanned (and skipped)"
        return f"Feed {feed} doesn't seem to be ok"

    def delete_feed(self, feed: str) -> str:
        if self.__storage.delete(feed):
            return f"Successfully removed feed {feed}"
        return f"Failed to remove feed {feed}"

    def update(self) -> list[ArticleInfo]:
        feeds = self.__restore()
        to_store = []
        retval = []
        for f in feeds:
            try:
                articles = f.get_new_articles()
                if articles:
                    to_store.append(f)
                    retval.extend(articles)
            except Exception as e:
                raise Exception(f"Error while retrieving {f.feed}: {str(e)}")
        self.__store(to_store)
        return retval

    def list_feeds(self) -> list[str]:
        return [f[0] for f in self.__storage.restore()]


class RssBot(commands.Cog):
    def __init__(self, bot, storage_file: str):
        self.__feeds = FeedCollection(storage_file)
        self.__bot = bot

    @tasks.loop(seconds=1200)
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

    @staticmethod
    def __site_name(url: str) -> str:
        if url.startswith("http"):
            url = url[url.find("//") + 2 :]
            if "/" in url:
                url = url[: url.find("/")]
        return url

    def add_site(self, what: str) -> str:
        error = ""
        try:
            site_name = RssBot.__site_name(what)
            r = requests.get(f"https://{site_name}/")
            tp = HtmlProcessor()
            tp.feed(r.text)
            if tp.rss_address:
                address = (
                    tp.rss_address
                    if tp.rss_address.startswith("http")
                    else f"https://{site_name}{tp.rss_address}"
                )
                return self.add_feed(address)
        except Exception as e:
            error = str(e)
        return f"Unable to parse {what} rss feed: {error}"

    def add_feed(self, what: str) -> str:
        try:
            return self.__feeds.add_feed(what)
        except Exception as e:
            return f"Unable to parse {what} rss feed: {str(e)}"

    def del_feed(self, what: str) -> str:
        try:
            return self.__feeds.delete_feed(what)
        except Exception as e:
            return f"Unable to parse {what} rss feed: {str(e)}"

    def list_feeds(self) -> str:
        try:
            feeds = self.__feeds.list_feeds()
            return "\n".join(feeds)
        except Exception as e:
            return f"Error reading feeds : {str(e)}"
