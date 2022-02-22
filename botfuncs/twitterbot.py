import twitter


class TwitterBot(object):
  def __init__(self, ck=None, cks=None, at=None, ats=None, throttle=60, users=[]):
    self.__ck = ck
    self.__cks = cks
    self.__at = at
    self.__ats = ats
    self.__api = None
    self.__since = {}
    self.__throttle = throttle
    self.__counter = 0
    self.__users = users

  def __reinit_api(self):
    self.__api = twitter.Api(consumer_key=self.__ck, consumer_secret=self.__cks,
                             access_token_key=self.__at, access_token_secret=self.__ats)

  def fetch_last_tweets(self, user):
    perform_send = user in self.__since
    kwargs = {'count': 20, 'screen_name': user, 'exclude_replies': True}
    if perform_send:
      kwargs['since_id'] = self.__since[user]
    res = []
    timeline = self.__api.GetUserTimeline(**kwargs)
    if timeline:
      self.__since[user] = timeline[0].id
      if perform_send:
        for msg in reversed(timeline):
          print('Received tweet: ', msg.text)
          if 'retweeted_status' in msg:
            res.append(('tweets', '{} retweet of https://twitter.com/{}/status/{} at https://twitter.com/{}/status/{}'.format(
                user, msg.retweeted_status.user.screen_name, msg.retweeted_status.id, user, msg.id)))
          else:
            res.append(('tweets', 'https://twitter.com/{}/status/{}'.format(user, msg.id)))
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
        self.__reinit_api()
      for u in self.__users:
        res.extend(self.fetch_last_tweets(u))
    except Exception as e:
      # res = [('tweets', "was ist das, kaput? pe twitter: {}".format(e))]
      res = []
      self.__api = None
    return res
