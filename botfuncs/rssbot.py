import html.parser as hp
import requests
import datetime
import dateutil.parser as dtparser
import xml.parsers.expat as expy
import dbm.gnu as gdbm
import json
from discord.ext import commands, tasks


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


class StorageData:
    guids: list[str] = []
    links: list[str] = []
    last_updated: datetime.datetime = datetime.datetime.min

    def __init__(self, data: dict = None):
        if data:
            self.guids = data['guids']
            self.links = data['links']
            self.last_updated = dtparser.parse(data['last_updated'])


class Storage:
    def __init__(self, path: str):
        self.__path = path

    def restore(self, feed: str) -> StorageData:
        try:
            with gdbm.open(self.__path, 'c') as db:
                result = StorageData(json.loads(db[feed]))
                print(f'restored: {len(result.guids)} guids')
                return result
        except Exception:
            pass
        return StorageData()

    def store(self, feed: str, data: StorageData) -> None:
        try:
            with gdbm.open(self.__path, 'c') as db:
                writer = json.dumps({'guids': data.guids, 'links': data.links,
                                     'last_updated': str(data.last_updated)})
                print(f'storing {len(data.guids)} guids: {writer}')
                db[feed] = writer
        except Exception as e:
            print(f'Unable to write to storage: {self.__path} feed: {feed}: {str(e)}')


class RssController:
    def __init__(self, url: str, store: Storage):
        self.__url = url
        self.__storage = store
        self.__storage_data = self.__storage.restore(url)

    def updated(self) -> bool:
        try:
            r = requests.head(self.__url)
            if r.ok:
                dt = dtparser.parse(r.headers['last-modified'])
                return dt > self.__storage_data.last_updated
        except Exception:
            print(f'Unable to reach {self.__url}')
        return False

    def __get_article_list(self, rss_feed):
        try:
            parser = RssParser()
            parser.parse(rss_feed)
            digest = parser.digest()
            print(f'Last build date: {digest.build_date}')
            return digest.articles
        except Exception:
            pass
        return []

    def update(self):
        count = 0
        try:
            r = requests.get(self.__url)
            if not r.ok:
                return
            articles = self.__get_article_list(r.content)
            for article in articles:
                new_article = False
                if article.guid:
                    new_article = article.guid not in self.__storage_data.guids
                else:
                    new_article = article.link not in self.__storage_data.links
                if new_article:
                    print(f'{article.pub_date} {article.title} {article.guid}')
                    count = count+1
                if article.guid:
                    self.__storage_data.guids.append(article.guid)
                else:
                    self.__storage_data.links.append(article.link)
        except Exception as e:
            print(f'Unable to process {self.__url} {str(e)}')
        print(f'{count} new articles found')
        if count > 0:
            self.__storage.store(self.__url, self.__storage_data)


class RssBot(commands.Cog):
    def __init__(self, storage_file: str):
        self.__storage_file = storage_file

    # async def fetch_last_tweets(self, user):
    #     perform_send = user in self.__since
    #     kwargs = {'count': 20, 'screen_name': user, 'exclude_replies': True}
    #     if perform_send:
    #         kwargs['since_id'] = self.__since[user]
    #     res = []
    #     timeline = self.__api.GetUserTimeline(**kwargs)
    #     if timeline:
    #         self.__since[user] = timeline[0].id
    #         if perform_send:
    #             for msg in reversed(timeline):
    #                 print('Received tweet: ', msg.text)
    #                 if 'retweeted_status' in msg._json:
    #                     screen_name = msg.retweeted_status.user.screen_name
    #                     status_id = msg.retweeted_status.id
    #                     res.append(
    #                         f'{user} retweet of https://twitter.com/{screen_name}/status/{status_id} at https://twitter.com/{user}/status/{msg.id}')
    #                 else:
    #                     res.append(f'https://twitter.com/{user}/status/{msg.id}')
    #         else:
    #             print('Last tweet:', timeline[0].id, timeline[0].text)
    #     return res

    # @tasks.loop(seconds=3600.0)
    # async def timer_function(self):
    #     try:
    #         if self.__api is None:
    #             await self.__reinit_api()
    #             if self.__api is not None:
    #                 await self.__bot.get_channel_by_name(name='robotest').send('M-am reconectat la Twitter')
    #         for u in self.__users:
    #             msg = await self.fetch_last_tweets(u)
    #             for m in msg:
    #                 await self.__bot.get_channel_by_name(name='tweets').send(m[:1900])
    #     except Exception as e:
    #         await self.__bot.get_channel_by_name(name='robotest').send(f'Twitter e din nou excepțional: {e}')
    #         self.__api = None
