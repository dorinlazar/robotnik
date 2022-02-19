import json
import yaml
import os
import twitter


def get_tweets(api=None, screen_name=None):
  timeline = api.GetUserTimeline(screen_name=screen_name, count=10)
  earliest_tweet = min(timeline, key=lambda x: x.id).id
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
  timeline = get_tweets(api=api, screen_name='mihaimaruseac')

  for tweet in timeline:
    if tweet.retweeted:
      print('retweeted status: ', tweet.retweeted_status.urls[0].expanded_url)
    # print(json.dumps(tweet._json))


# {"created_at": "Fri Feb 18 14:34:41 +0000 2022", "id": 1494681782544789507, "id_str": "1494681782544789507", "text": "RT @MaggieAstor: At the 2000 Olympics, Andreea Raducan was stripped of her all-around gold medal because she woke up with a cold and the Ro\u2026", "truncated": false, "entities": {"hashtags": [], "symbols": [], "user_mentions": [{"screen_name": "MaggieAstor", "name": "Maggie Astor", "id": 326562333, "id_str": "326562333", "indices": [3, 15]}], "urls": []}, "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>", "in_reply_to_status_id": null, "in_reply_to_status_id_str": null, "in_reply_to_user_id": null, "in_reply_to_user_id_str": null, "in_reply_to_screen_name": null, "user": {"id": 23897807, "id_str": "23897807", "name": "Mihai Maruseac", "screen_name": "mihaimaruseac", "location": "Mountain View, CA", "description": "At Google making tensors flow safely.\n\nPreviously at startup making ML algos be differentially private.\n\nWriting Haskell for fun when I get time.", "url": null, "entities": {"description": {"urls": []}}, "protected": false, "followers_count": 1158, "friends_count": 1001, "listed_count": 27, "created_at": "Thu Mar 12 04:27:52 +0000 2009", "favourites_count": 50199, "utc_offset": null, "time_zone": null, "geo_enabled": true, "verified": false, "statuses_count": 11014, "lang": null, "contributors_enabled": false, "is_translator": false, "is_translation_enabled": false, "profile_background_color": "131516", "profile_background_image_url": "http://abs.twimg.com/images/themes/theme14/bg.gif", "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme14/bg.gif", "profile_background_tile": true, "profile_image_url": "http://pbs.twimg.com/profile_images/1306795040019066881/ftp-sYVp_normal.jpg", "profile_image_url_https": "https://pbs.twimg.com/profile_images/1306795040019066881/ftp-sYVp_normal.jpg", "profile_banner_url": "https://pbs.twimg.com/profile_banners/23897807/1440197215", "profile_link_color": "ABB8C2", "profile_sidebar_border_color": "EEEEEE", "profile_sidebar_fill_color": "EFEFEF", "profile_text_color": "333333", "profile_use_background_image": false, "has_extended_profile": true, "default_profile": false, "default_profile_image": false, "following": true, "follow_request_sent": false, "notifications": false, "translator_type": "none", "withheld_in_countries": []}, "geo": null, "coordinates": null, "place": null, "contributors": null, "retweeted_status": {"created_at": "Wed Feb 16 01:27:01 +0000 2022", "id": 1493758783851417605, "id_str": "1493758783851417605", "text": "At the 2000 Olympics, Andreea Raducan was stripped of her all-around gold medal because she woke up with a cold and\u2026 https://t.co/eR61K6yKI2", "truncated": true, "entities": {"hashtags": [], "symbols": [], "user_mentions": [], "urls": [{"url": "https://t.co/eR61K6yKI2", "expanded_url": "https://twitter.com/i/web/status/1493758783851417605", "display_url": "twitter.com/i/web/status/1\u2026", "indices": [117, 140]}]}, "source": "<a href=\"https://mobile.twitter.com\" rel=\"nofollow\">Twitter Web App</a>", "in_reply_to_status_id": null, "in_reply_to_status_id_str": null, "in_reply_to_user_id": null, "in_reply_to_user_id_str": null, "in_reply_to_screen_name": null, "user": {"id": 326562333, "id_str": "326562333", "name": "Maggie Astor", "screen_name": "MaggieAstor", "location": "New York, N.Y.", "description": "Reporter @nytimes, politics/covid/live news/a bit of everything. Stay for cat photos and gymnastics. Not one of those Astors. She/her, maggie.astor@nytimes.com.", "url": "https://t.co/u61fWoOGKS", "entities": {"url": {"urls": [{"url": "https://t.co/u61fWoOGKS", "expanded_url": "https://www.nytimes.com/by/maggie-astor", "display_url": "nytimes.com/by/maggie-astor", "indices": [0, 23]}]}, "description": {"urls": []}}, "protected": false, "followers_count": 21080, "friends_count": 1518, "listed_count": 413, "created_at": "Thu Jun 30 03:36:13 +0000 2011", "favourites_count": 4053, "utc_offset": null, "time_zone": null, "geo_enabled": false, "verified": true, "statuses_count": 7742, "lang": null, "contributors_enabled": false, "is_translator": false, "is_translation_enabled": false, "profile_background_color": "C0DEED", "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "profile_background_tile": false, "profile_image_url": "http://pbs.twimg.com/profile_images/1280172404506087424/qmeNwwMm_normal.jpg", "profile_image_url_https": "https://pbs.twimg.com/profile_images/1280172404506087424/qmeNwwMm_normal.jpg", "profile_banner_url": "https://pbs.twimg.com/profile_banners/326562333/1547161725", "profile_link_color": "1DA1F2", "profile_sidebar_border_color": "C0DEED", "profile_sidebar_fill_color": "DDEEF6", "profile_text_color": "333333", "profile_use_background_image": true, "has_extended_profile": true, "default_profile": true, "default_profile_image": false, "following": false, "follow_request_sent": false, "notifications": false, "translator_type": "none", "withheld_in_countries": []}, "geo": null, "coordinates": null, "place": null, "contributors": null, "is_quote_status": false, "retweet_count": 94, "favorite_count": 384, "favorited": true, "retweeted": true, "possibly_sensitive": false, "lang": "en"}, "is_quote_status": false, "retweet_count": 94, "favorite_count": 0, "favorited": true, "retweeted": true, "lang": "en"}
