import html.parser as hp
import requests
import datetime
import dateutil.parser as dtparser
import xml.parsers.expat as expy
import dbm.gnu as gdbm
import json
from discord.ext import commands, tasks


class TestParser(hp.HTMLParser):
    def __init__(self):
        super().__init__()
        self.__rss_address = ''

    @property
    def rss_address(self): return self.__rss_address

    def __process_attributes(self, attrs: list[tuple[str, str | None]]) -> None:
        found_alternate = False
        found_rss = False
        href = ''
        for t in attrs:
            if t:
                if t[0] == 'rel' and t[1] == 'alternate':
                    found_alternate = True
                if t[0] == 'type' and t[1] == 'application/rss+xml':
                    found_rss = True
                if t[0] == 'href':
                    href = t[1]
        if found_alternate and found_rss and href:
            self.__rss_address = href
            # self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'link':
            self.__process_attributes(attrs)


class ArticleInfo:
    title: str
    link: str
    guid: str
    pub_date: datetime.datetime


class FeedDigest:
    build_date: datetime.datetime = datetime.datetime.min
    articles: list[ArticleInfo] = []


class RssParser:
    def __init__(self):
        self.__parser = expy.ParserCreate()
        self.__parser.StartElementHandler = self.__start_element
        self.__parser.EndElementHandler = self.__end_element
        self.__parser.CharacterDataHandler = self.__char_data
        self.__in_channel = False
        self.__in_item = False
        self.__current_element = None
        self.__current_data = ''
        self.__feed_digest = FeedDigest()

    def parse(self, content: str):
        self.__parser.Parse(content, 1)

    def __start_element(self, name: str, attrs: dict[str, str]):
        if not self.__in_channel:
            self.__in_channel = name == 'channel'
            return
        if not self.__in_item:
            self.__in_item = name == 'item'
            if self.__in_item:
                self.__current_element = ArticleInfo()
        self.__current_data = ''

    def __end_element(self, name: str):
        if self.__in_item:
            if name == 'item':
                self.__in_item = False
                if self.__current_element and self.__current_element.link:
                    self.__feed_digest.articles.append(self.__current_element)
            else:
                match(name):
                    case 'link':
                        self.__current_element.link = self.__current_data
                    case 'pubDate':
                        self.__current_element.pub_date = dtparser.parse(self.__current_data)
                    case 'guid':
                        self.__current_element.guid = self.__current_data
                    case 'title':
                        self.__current_element.title = self.__current_data
        else:
            if name == 'lastBuildDate':
                self.__feed_digest.build_date = dtparser.parse(self.__current_data)
        if self.__in_channel:
            if name == 'channel':
                self.__in_channel = False

    def __char_data(self, data: str):
        self.__current_data += data

    def digest(self): return self.__feed_digest


class FeedData:
    guids: list[str] = []
    links: list[str] = []
    last_updated: datetime.datetime = datetime.datetime.min
    feed: str = ''

    def __init__(self, f: str, data: dict = None):
        self.feed = f
        if data:
            self.guids = data['guids']
            self.links = data['links']
            self.last_updated = dtparser.parse(data['last_updated'])

    def to_json(self) -> str:
        return json.dumps({'guids': self.guids, 'links': self.links,
                           'last_updated': str(self.last_updated)})

    def __get_article_list(self, rss_feed):
        parser = RssParser()
        parser.parse(rss_feed)
        digest = parser.digest()
        print(f'Last build date: {digest.build_date}')
        return digest.articles

    def __updated(self) -> bool:
        try:
            r = requests.head(self.feed)
            if r.ok:
                dt = dtparser.parse(r.headers['last-modified'])
                return dt > self.last_updated
        except Exception:
            print(f'Unable to reach {self.__url}')
        return False

    def update(self) -> list[ArticleInfo]:
        if not self.__updated():
            return []

        retval = []
        r = requests.get(self.__url)
        if not r.ok:
            return
        articles = self.__get_article_list(r.content)
        for article in articles:
            new_article = False
            if article.guid:
                new_article = article.guid not in self.guids
            else:
                new_article = article.link not in self.links
            if new_article:
                retval.append(article)
                if article.guid:
                    self.guids.append(article.guid)
                else:
                    self.links.append(article.link)
        print(f'{len(retval)} new articles found in {self.feed}')
        return retval


class FeedCollection:
    def __init__(self, storage_file: str):
        self.__path = storage_file

    def __restore(self) -> list[FeedData]:
        feeds = []
        try:
            with gdbm.open(self.__path) as db:
                keys = []
                key = db.firstkey()
                while key is not None:
                    keys.append(key)
                    key = db.nextkey()
                for key in keys:
                    feeds.append(FeedData(key, json.loads(db[key])))
        except Exception:
            pass
        return feeds

    def __store(self, feeds: list[FeedData]) -> None:
        try:
            with gdbm.open(self.__path, 'c') as db:
                for f in feeds:
                    db[f.feed] = json.dumps(f.to_json())
        except Exception:
            pass

    def add_feed(self, feed: str) -> str:
        feed_data = FeedData(feed)
        articles = feed_data.update()
        if articles:
            self.__store([feed_data])
            return f'Feed {feed} successfully added, {len(articles)} pre-scanned (and skipped)'
        else:
            return f'Feed {feed} doesn''t seem to be ok'

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
                raise RuntimeError(error=f'Error while retrieving {f.feed}: {str(e)}')
        self.__store(to_store)
        return retval


class RssBot(commands.Cog):
    def __init__(self, storage_file: str):
        self.__feeds = FeedCollection(storage_file)

    @tasks.loop(hours=1)
    async def timer_function(self):
        try:
            updates = self.__feeds.update()
            for item in updates:
                message = f'{item.title} {item.link}'
                await self.__bot.get_channel_by_name(name='tweets').send(message[:1900])
        except Exception as e:
            await self.__bot.get_channel_by_name(name='robotest').send(f'Am căzut și m-am împiedicat în RSS-uri: {e}')

    def add_site(self, what: str) -> str:
        error = ''
        try:
            if what.startswith('http'):
                what = what[what.find('//')+2:]
                if '/' in what:
                    what = what[:what.find('/')]
            r = requests.get(f'https://{what}/')
            tp = TestParser()
            tp.feed(r.text)
            if tp.rss_address:
                address = tp.rss_address if tp.rss_address.startswith('http') else f'https://{what}{tp.rss_address}'
                return self.add_site(address)
        except Exception as e:
            error = str(e)
        return f'Unable to parse {what} rss feed: {error}'

    def add_feed(self, what: str) -> str:
        return self.__feeds.add_feed(what)
