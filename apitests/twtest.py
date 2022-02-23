import json
import yaml
import os
import twitter


def get_tweets(api=None, screen_name=None):
  timeline = api.GetUserTimeline(screen_name=screen_name, count=10)
  return timeline
  # print("getting tweets before:", earliest_tweet)

  # while True:
  #   tweets = api.GetUserTimeline(
  #       screen_name=screen_name, max_id=earliest_tweet, count=200
  #   )
  #   new_earliest = min(tweets, key=lambda x: x.id).id

  #   if not tweets or new_earliest == earliest_tweet:
  #     break
  #   else:
  #     earliest_tweet = new_earliest
  #     print("getting tweets before:", earliest_tweet)
  #     timeline += tweets

  # return timeline


if __name__ == "__main__":
  with open(os.path.expanduser('~/.robotnik.yml'), 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
  tw = cfg['twitter']
  api = twitter.Api(
      tw['ck'], tw['cks'], tw['at'], tw['ats']
  )
  timeline = get_tweets(api=api, screen_name='dorinlazar')

  for tweet in timeline:
    # print(json.dumps(tweet._json))
    if 'retweeted_status' in tweet._json:
      print('retweeted status: https://twitter.com/{}/status/{}'.format(tweet.retweeted_status.user.screen_name, tweet.retweeted_status.id))
