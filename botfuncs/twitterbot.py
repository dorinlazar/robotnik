import twitter
api = twitter.Api(consumer_key=ck, consumer_secret=cks, access_token_key=at, access_token_secret=ats)

timeline = api.GetUserTimeline(screen_name='dorinlazar', count=200)
