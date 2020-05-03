import twitter


class TwitterBot(object):
  def __init__(self, ck, cks, at, ats):
    self.__api = twitter.Api(consumer_key=ck, consumer_secret=cks, access_token_key=at, access_token_secret=ats)
    self.__since = None
    self.__throttle = 60
    self.__counter = 0

  def on_timer(self):
    self.__counter = self.__counter + 1
    if self.__counter < self.__throttle:
      return []
    self.__counter = 0
    perform_send = self.__since is not None
    kwargs = {'count': 20, 'screen_name': 'dorinlazar', 'exclude_replies': True}
    if perform_send:
      kwargs['since_id'] = self.__since
    timeline = self.__api.GetUserTimeline(**kwargs)
    res = []
    if timeline and perform_send:
      self.__since = timeline[0].id
      for msg in reversed(timeline):
        res.append(('tweets', '{} https://twitter.com/i/web/status/{}'.format('RT' if msg.retweeted else 'TW',  msg.id)))
    return res