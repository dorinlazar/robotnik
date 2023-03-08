import twitter
from discord.ext import commands, tasks


class TwitterBot(commands.Cog):
    def __init__(self, bot=None, ck=None, cks=None, at=None, ats=None, users=[]):
        self.__ck = ck
        self.__cks = cks
        self.__at = at
        self.__ats = ats
        self.__api = None
        self.__since = {}
        self.__users = users
        self.__bot = bot

    async def __reinit_api(self):
        self.__api = twitter.Api(consumer_key=self.__ck, consumer_secret=self.__cks,
                                 access_token_key=self.__at, access_token_secret=self.__ats)

    async def fetch_last_tweets(self, user):
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
                    if 'retweeted_status' in msg._json:
                        screen_name = msg.retweeted_status.user.screen_name
                        status_id = msg.retweeted_status.id
                        res.append(
                            f'{user} retweet of https://twitter.com/{screen_name}/status/{status_id} at https://twitter.com/{user}/status/{msg.id}')
                    else:
                        res.append(f'https://twitter.com/{user}/status/{msg.id}')
            else:
                print('Last tweet:', timeline[0].id, timeline[0].text)
        return res

    @tasks.loop(seconds=60.0)
    async def timer_function(self):
        try:
            if self.__api is None:
                await self.__reinit_api()
                if self.__api is not None:
                    await self.__bot.get_channel_by_name(name='robotest').send('M-am reconectat la Twitter')
            for u in self.__users:
                msg = await self.fetch_last_tweets(u)
                for m in msg:
                    await self.__bot.get_channel_by_name(name='tweets').send(m[:1900])
        except Exception as e:
            await self.__bot.get_channel_by_name(name='robotest').send(f'Twitter e din nou excepțional: {e}')
            self.__api = None
