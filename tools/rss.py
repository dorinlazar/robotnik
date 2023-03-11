import datetime
import xml.parsers.expat as expy
import dateutil.parser as dtparser
import json


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
                if self.last_updated == datetime.datetime.min:
                    return True
                dt = dtparser.parse(r.headers['last-modified'])
                return dt > self.last_updated
        except Exception as e:
            print(f'Unable to reach {self.feed}: {str(e)}')
        return False

    def update(self) -> list[ArticleInfo]:
        if not self.__updated():
            return []

        retval = []
        r = requests.get(self.feed)
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


if __name__ == '__main__':
    import requests
    address = f'https://dorinlazar.ro/index.xml'
    r = requests.get(address)
    parser = RssParser()
    parser.parse(r.content)
    digest = parser.digest()
    print(f'Last build time: {digest.build_date}')
    for article in digest.articles:
        print(f'Article: {article.title} on {article.pub_date}: {article.link}')
