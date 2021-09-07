from justwatch import JustWatch
from roboapi import MessageHandler


class JustWatchBot(MessageHandler):
  def shortcode(self) -> str: return 'movie'

  def on_message(self, msg):
    country = 'RO'
    spl = msg.split()
    if len(spl[0]) == 2 and spl[0].upper() == spl[0]:
      country = spl[0]
      msg = ' '.join(spl[1:])
    just_watch = JustWatch(country=country)
    results = just_watch.search_for_item(query=msg)
    if type(results) == dict and 'items' in results and len(results['items']) > 0:
      return self.to_info_display(results['items'][0], msg)
    return 'N-am găsit niciun film cu numele [' + msg + ']'

  def to_info_display(self, info, msg):
    urls = list(set([u['urls']['standard_web'] for u in info['offers']]))
    imdb_info = next(filter(lambda x: x['provider_type'] == 'imdb:score', info['scoring']))
    imdb_text = '' if imdb_info is None else 'IMDB: ' + str(imdb_info['value'])
    next(filter(lambda x: x['provider_type'] == 'imdb:score', info['scoring']))['value']
    return 'Căutare: ' + msg + '\nTitlu: [' + info['title'] + '] ' + imdb_text + '\n' + '\n'.join(urls)
