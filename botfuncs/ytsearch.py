from youtubesearchpython import VideosSearch

class YTSearch(object):
    def shortcode(self) -> str: return 'yt'

    def on_request(self, msg):
        country = 'RO'
        spl = msg.split()
        if len(spl[0]) == 2 and spl[0].upper() == spl[0]:
            country = spl[0]
            msg = ' '.join(spl[1:])

        runner = VideosSearch(msg, limit=1, region=country)
        x = runner.result()
        return self.__to_info_display(x['result'][0])

    def __to_info_display(self, info):
        return info['accessibility']['title'] + '\nhttps://youtu.be/' + info['id']
