from datetime import datetime as dtime
import xml.parsers.expat as expy
from dataclasses import dataclass
import dateutil.parser as dtparser
from dateutil.tz import tzutc
import json
import requests
from typing import Optional, Any


class ArticleInfo:
    def __init__(self):
        self.__title: str = ""
        self.__link: str = ""
        self.__guid: str = ""
        self.__pub_date: dtime = dtime.min.replace(tzinfo=tzutc())

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, value: str):
        self.__title = value

    @property
    def link(self) -> str:
        return self.__link

    @link.setter
    def link(self, value: str):
        self.__link = value

    @property
    def guid(self) -> str:
        return self.__guid

    @guid.setter
    def guid(self, value: str):
        self.__guid = value

    @property
    def pub_date(self) -> dtime:
        return self.__pub_date

    @pub_date.setter
    def pub_date(self, value: dtime):
        self.__pub_date = value


class FeedDigest:
    def __init__(self):
        self.__build_date = dtime.min.replace(tzinfo=tzutc())
        self.__articles: list[ArticleInfo] = []

    @property
    def articles(self) -> list[ArticleInfo]:
        return self.__articles

    @articles.setter
    def articles(self, value: list[ArticleInfo]):
        self.__articles = value

    @property
    def build_date(self) -> dtime:
        return self.__build_date

    @build_date.setter
    def build_date(self, value: dtime):
        self.__build_date = value


@dataclass
class FeedSystem:
    name: str
    channel_tag_name: str
    item_name: str
    last_build_date_name: str
    guid_name: str


def create_rss_system() -> FeedSystem:
    return FeedSystem(
        name="RSS",
        channel_tag_name="channel",
        item_name="item",
        last_build_date_name="lastBuildDate",
        guid_name="guid",
    )


def create_atom_system() -> FeedSystem:
    return FeedSystem(
        name="ATOM",
        channel_tag_name="feed",
        item_name="entry",
        last_build_date_name="updated",
        guid_name="id",
    )


def create_system(type: str) -> FeedSystem:
    if type == "RSS":
        return create_rss_system()
    if type == "ATOM":
        return create_atom_system()
    raise Exception(f"Invalid system: {type}")


class RssParser:
    def __init__(self):
        self.__parser = expy.ParserCreate()
        self.__parser.StartElementHandler = self.__start_element
        self.__parser.EndElementHandler = self.__end_element
        self.__parser.CharacterDataHandler = self.__char_data
        self.__in_channel = False
        self.__in_item = False
        self.__current_element: ArticleInfo
        self.__current_data: str = ""
        self.__feed_digest = FeedDigest()
        self.__system: FeedSystem = create_system("RSS")
        print(f"{len(self.__feed_digest.articles)} already found?")

    def parse(self, content: str) -> None:
        self.__parser.Parse(content, True)

    def __start_element(self, name: str, attrs: dict[str, str]):
        if name == "feed" and attrs.get("xmlns", "") == "http://www.w3.org/2005/Atom":
            self.__system = create_system("ATOM")
        if name == "rss" and attrs.get("version", "") == "2.0":
            self.__system = create_system("RSS")
        if not self.__in_channel:
            self.__in_channel = name == self.__system.channel_tag_name
            return
        if not self.__in_item:
            self.__in_item = name == self.__system.item_name
            if self.__in_item:
                self.__current_element = ArticleInfo()
        self.__current_data = ""

    def __end_element(self, name: str):
        if self.__in_item:
            if name == self.__system.item_name:
                self.__in_item = False
                if self.__current_element and self.__current_element.link:
                    self.__feed_digest.articles.append(self.__current_element)
            else:
                match (name):
                    case "link":
                        self.__current_element.link = self.__current_data
                    case "pubDate":
                        self.__current_element.pub_date = dtparser.parse(
                            self.__current_data
                        ).replace(tzinfo=tzutc())
                    case self.__system.guid_name:
                        self.__current_element.guid = self.__current_data
                    case "title":
                        self.__current_element.title = self.__current_data
        else:
            if name == self.__system.last_build_date_name:
                self.__feed_digest.build_date = dtparser.parse(
                    self.__current_data
                ).replace(tzinfo=tzutc())
        if self.__in_channel and name == self.__system.channel_tag_name:
            self.__in_channel = False

    def __char_data(self, data: str):
        self.__current_data += data

    def digest(self, update_time: dtime = dtime.utcnow().replace(tzinfo=tzutc())):
        if self.__feed_digest.build_date == dtime.min.replace(tzinfo=tzutc()):
            self.__feed_digest.build_date = update_time
        return self.__feed_digest


class FeedFetcher:
    @staticmethod
    def url_last_modified(url: str) -> dtime:
        try:
            r = requests.head(url)
            if r.ok:
                if "last-modified" in r.headers:
                    return dtparser.parse(r.headers["last-modified"]).replace(
                        tzinfo=tzutc()
                    )
                return dtime.now(tz=tzutc())
        except Exception as e:
            print(f"Unable to reach url {url}: {str(e)}")
        return dtime.min.replace(tzinfo=tzutc())

    @staticmethod
    def get_content(url: str) -> str:
        try:
            r = requests.get(url)
            if r.ok:
                return r.content.decode()
        except Exception as e:
            print(f"Unable to reach url {url}: {str(e)}")
        return ""


class FeedData:
    def __init__(self, feed: str, stored_data: Optional[dict[str, Any]] = None):
        self.__feed = feed
        self.__article_ids: set[str] = set()
        self.__last_updated: dtime = dtime.min.replace(tzinfo=tzutc())
        self.__last_touched: dtime = dtime.min.replace(tzinfo=tzutc())
        self.__destination: str = "#shorts"
        if stored_data:
            self.__article_ids = set(stored_data["ids"])
            self.__last_updated = dtparser.parse(stored_data["last_updated"]).replace(
                tzinfo=tzutc()
            )
            self.__destination = stored_data["dest"]

    @property
    def feed(self) -> str:
        return self.__feed

    def to_json(self) -> str:
        return json.dumps(
            {
                "ids": list(self.__article_ids),
                "last_updated": str(self.__last_updated),
                "dest": self.__destination,
            }
        )

    def __get_digest(self, rss_feed_content: str) -> FeedDigest:
        parser = RssParser()
        parser.parse(rss_feed_content)
        digest = parser.digest(self.__last_touched)
        print(f"Last build date: {digest.build_date}")
        return digest

    def __updated(self) -> bool:
        self.__last_touched = FeedFetcher.url_last_modified(self.__feed)
        return self.__last_touched > self.__last_updated

    def get_new_articles(self) -> list[ArticleInfo]:
        if not self.__updated():
            return []

        retval: list[ArticleInfo] = []
        feed_content = FeedFetcher.get_content(self.__feed)
        digest = self.__get_digest(feed_content)
        if digest.build_date > self.__last_updated:
            articles: dict[str, ArticleInfo] = dict()
            for article in digest.articles:
                id = article.guid if article.guid else article.link
                articles[id] = article
            new_ids = set(articles.keys())
            new_items = new_ids - self.__article_ids
            self.__article_ids = new_ids
            self.__last_updated = digest.build_date
            retval = [articles[name] for name in new_items]
        print(f"{len(retval)} new articles found in {self.__feed}")
        return retval


def __test01():
    import requests

    address = "https://krossfire.ro/feed/"
    r = requests.get(address)
    parser = RssParser()
    parser.parse(r.content.decode())
    digest = parser.digest()
    print(f"Last build time: {digest.build_date}")
    for article in digest.articles:
        print(f"Article: {article.title} on {article.pub_date}: {article.link}")


def __test03():
    feed_data = FeedData("https://world-nuclear-news.org/?rss=FullFeed")
    updates = feed_data.get_new_articles()
    for article in updates:
        print(f"Article: {article.title} on {article.pub_date}: {article.link}")


def __test02():
    feed_data = FeedData("https://dorinlazar.ro/index.xml")
    updates = feed_data.get_new_articles()
    for article in updates:
        print(f"Article: {article.title} on {article.pub_date}: {article.link}")
    updates = feed_data.get_new_articles()
    print(f">> Second reading, {len(updates)} updates found")
    feed_data2 = FeedData("https://mastodon.social/@dorinlazar.rss")
    updates2 = feed_data2.get_new_articles()
    for article in updates2:
        print(f"Article: {article.title} on {article.pub_date}: {article.link}")
    updates2 = feed_data.get_new_articles()
    print(f">> Second reading, {len(updates2)} updates found")


if __name__ == "__main__":
    __test01()
