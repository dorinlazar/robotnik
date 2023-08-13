import html.parser as hp


class HtmlProcessor(hp.HTMLParser):
    def __init__(self):
        super().__init__()
        self.rss_address = ""

    def __process_attributes(self, attrs: list[tuple[str, str | None]]) -> None:
        found_alternate = False
        found_rss = False
        href = ""
        for t in attrs:
            if t:
                if t[0] == "rel" and t[1] == "alternate":
                    found_alternate = True
                if t[0] == "type" and t[1] == "application/rss+xml":
                    found_rss = True
                if t[0] == "href":
                    href = t[1]
        if found_alternate and found_rss and href:
            self.rss_address = href

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "link":
            self.__process_attributes(attrs)


class HtmlTextFilter(hp.HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data
