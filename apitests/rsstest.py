import html.parser as hp
import requests
import datetime
import dateutil.parser as dtparser
import xml.parsers.expat as expy


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


def test_run(site: str):
    r = requests.get(f'https://{site}/')
    print(f'read {site}: {r.status_code}')
    tp = TestParser()
    tp.feed(r.text)
    if tp.rss_address:
        address = tp.rss_address if tp.rss_address.startswith('http') else f'https://{site}{tp.rss_address}'
        print(f'Identified rss feed: {address}')
    else:
        print(f'Rss feed not found')


@dataclass
class ArticleInfo:
    link: str
    guid: str
    pub_date: datetime.datetime


class RssParser:
    def __init__(self):
        self.__parser = expy.ParserCreate()
        self.__parser.StartElementHandler = self.__start_element
        self.__parser.EndElementHandler = self.__end_element
        self.__parser.CharacterDataHandler = self.__char_data
        self.__in_channel = False
        self.__in_item = False
        self.__in_link = False
        self.__in_pub_date = False
        self.__in_guid = False
        self.__current_element = None

    def __start_element(self, name: str, attrs: dict[str, str]]):
        if not self.__in_channel:
            self.__in_channel = name == 'channel'
            return
        if not self.__in_item:
            self.__in_item= name == 'item'
            if self.__in_item:
                self.__current_element= ArticleInfo()
            return
        self.__in_link = name == 'link'
        self.__in_guid = name == 'guid'
        self.__in_pub_date = name == 'pubDate'
    def __end_element(self, name: str):
        self.__in_link = False
        self.__in_guid = False
        self.__in_pub_date = False
        if self.__in_item:
            if name == 'item': self.__in_item= False
        if self.__in_channel:
            if name == 'channel': self.__in_channel= False
    def __char_data(self, data: str):







class RssController:
    def __init__(self, url: str):
        self.__url = url
        self.__last_updated = datetime.datetime.min()

    def updated(self) -> bool:
        try:
            r = requests.head(self.__url)
            if r.ok:
                dt = dtparser.parse(r.headers['last-modified'])
                return dt > self.__last_updated
        except Exception:
            print(f'Unable to reach {self.__url}')
        return False

    def __get_article_list(self, rss_feed):
        try:
            parser = expy.ParserCreate()
            parser.StartElementHandler
        except Exception:
            pass
        return []

    def update(self, notifier: callable[str]):
        try:
            r = requests.get(self.__url)
            if not r.ok:
                return
            articles = self.__get_article_list(r.content)
            for article in articles:
                print(f'{article.timestamp} {article.title} {article.id}')
        except Exception:
            print(f'Unable to process {self.__url}')


if __name__ == '__main__':
    test_run('dorinlazar.ro')
