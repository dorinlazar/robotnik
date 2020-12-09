import twitter
import html
import threading


class TwitterBot(object):
  def __init__(self, ck=None, cks=None, at=None, ats=None, throttle=60, users=[]):
    self.__ck = ck
    self.__cks = cks
    self.__at = at
    self.__ats = ats
    self.__api = twitter.Api(consumer_key=ck, consumer_secret=cks, access_token_key=at, access_token_secret=ats)
    self.__since = {}
    self.__throttle = throttle
    self.__counter = 0
    self.__users = users

  def fetch_last_tweets(self, user):
    perform_send = user in self.__since
    kwargs = {'count': 20, 'screen_name': user, 'exclude_replies': True}
    if perform_send:
      kwargs['since_id'] = self.__since[user]
    timeline = self.__api.GetUserTimeline(**kwargs)
    res = []
    if timeline:
      self.__since[user] = timeline[0].id
      if perform_send:
        for msg in reversed(timeline):
          print('Received tweet: ', msg.text)
          res.append(('tweets', '{} {}{} {}'.format(user, 'RT ' if msg.retweeted else '', html.unescape(msg.text),
                                                    'https://twitter.com/i/web/status/{}'.format(msg.id) if msg.truncated or len(msg.urls) == 0 else '')))
      else:
        print('Last tweet:', timeline[0].id, timeline[0].text)
    return res

  def on_timer(self):
    self.__counter = self.__counter - 1
    if self.__counter > 0:
      return []
    self.__counter = self.__throttle
    res = []
    try:
      if self.__api is None:
        self.__api = twitter.Api(consumer_key=self.__ck, consumer_secret=self.__cks,
                                 access_token_key=self.__at, access_token_secret=self.__ats)
      for u in self.__users:
        res.extend(self.fetch_last_tweets(u))
    except Exception as e:
      res = ["crăpași pe twitter: {0}".format(e)]
      self.__api = None
    return res
