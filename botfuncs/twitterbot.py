import twitter


class TwitterBot(object):
  def __init__(self, ck, cks, at, ats):
    self.__api = twitter.Api(consumer_key=ck, consumer_secret=cks, access_token_key=at, access_token_secret=ats)
    self.__since = None
    self.__throttle = 60
    self.__counter = 0

  def on_timer(self):
    self.__counter = self.__counter - 1
    if self.__counter > 0:
      return []
    self.__counter = self.__throttle
    perform_send = self.__since is not None
    kwargs = {'count': 20, 'screen_name': 'dorinlazar', 'exclude_replies': True}
    if perform_send:
      kwargs['since_id'] = self.__since
    timeline = self.__api.GetUserTimeline(**kwargs)
    res = []
    if timeline:
      self.__since = timeline[0].id
      if perform_send:
        for msg in reversed(timeline):
          print('Received tweet: ', msg.text)
          res.append(('tweets', '{} {}'.format('RT' if msg.retweeted else 'TW',
                                               'https://twitter.com/i/web/status/{}'.format(msg.id) if msg.truncated else msg.text)))
      else:
        print('Last tweet:', timeline[0].id, timeline[0].text)
    return res
