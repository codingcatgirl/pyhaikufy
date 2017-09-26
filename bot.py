import json
import time
import traceback
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread

import tweepy

from haikufy import Haikufy


class StreamListener(tweepy.StreamListener):
    def __init__(self, dispatcher, screen_name):
        super(StreamListener, self).__init__(None)
        self.screen_name = screen_name
        self.dispatcher = dispatcher
        self.haikufy = Haikufy()
        print('[StreamListener] connected!')

    def on_status(self, tweet):
        print('[StreamListener] ran on_status')

    def on_error(self, status_code):
        print('[StreamListener] Error: ' + repr(status_code))
        return False

    def on_data(self, rawdata):
        data = json.loads(rawdata)

        if (data.get('event') == 'follow' and
                data.get('target', {}).get('screen_name').lower() == self.screen_name.lower()):
            user_id = data.get('source', {}).get('id_str', '')
            user_name = data.get('source', {}).get('name', '')
            screen_name = data.get('source', {}).get('screen_name', '')
            print('[StreamListener] we were followed by %s (@%s), refollow!' % (user_name, screen_name))
            self.dispatcher.api.create_friendship(user_id=user_id)
            return

        if 'in_reply_to_status_id' not in data or 'retweeted_status' in data:
            return

        text = data.get('text', '')
        user_name = data.get('user', {}).get('name', '')
        screen_name = data.get('user', {}).get('screen_name', '')
        status_id = data.get('id_str', None)

        if screen_name.lower() == self.screen_name.lower():
            return

        print('[StreamListener] incoming tweet from %s (@%s):' % (user_name, screen_name))
        print('[StreamListener] '+repr(text))

        leading_mentions = ['@'+screen_name]
        text = text.split()
        while text and text[0].startswith('@'):
            leading_mentions.append(text.pop(0))
        while text and (text[-1].startswith('http://') or text[-1].startswith('https://')):
            text.pop()
        text = ' '.join(text)

        try:
            haiku = self.haikufy.haikufy(text)
        except:
            traceback.print_exc()
            print('[StreamListener] Error. Ignoring tweet.')
            return

        if haiku is None:
            print('[StreamListener] Not a haiku.')
            return

        print('[StreamListener] This is a haiku, queue reply!')
        self.dispatcher.tweet(text=' '.join(leading_mentions)+'\n'+haiku, in_reply_to=status_id)


class TweetDispatcher:
    time_between_tweets = timedelta(seconds=42)

    def __init__(self, api):
        self.api = api
        self.last_tweet = datetime.now() - timedelta(seconds=15)
        self.tweet_queue = Queue()

    def run(self):
        while True:
            wait_seconds = (self.time_between_tweets-(datetime.now()-self.last_tweet)).total_seconds()
            if wait_seconds > 0:
                print('[TweetDispatcher] wait for %ds to satisfy the rate limit…' % wait_seconds)
                time.sleep(wait_seconds)
            else:
                time.sleep(1)

            print('[TweetDispatcher] ready to tweet again!')

            try:
                text, in_reply_to, state, filename_prefix = self.tweet_queue.get()
                print('[TweetDispatcher] tweeting:\n'+text)
                kwargs = {}
                if in_reply_to is not None:
                    kwargs['in_reply_to_status_id'] = in_reply_to
                self.last_tweet = datetime.now()
                status = self.api.update_status(text, **kwargs)
            except:
                print('[TweetDispatcher] Oh no, something went wrong!')
                traceback.print_exc()

    def tweet(self, text, in_reply_to=None, state=None, filename_prefix=''):
        print('[TweetDispatcher] Queueing tweet:\n%s' % text)
        self.tweet_queue.put((text, in_reply_to, state, filename_prefix))


def start_stream(auth, dispatcher, screen_name):
    lastconnect = 0
    wait = 60
    while True:
        if lastconnect + 60 >= time.time():
            print('[StreamListener] waiting to reconnect…')
            time.sleep(wait)
            wait = wait * 2
        else:
            wait = 90
        lastconnect = time.time()
        tweepy.Stream(auth=auth, listener=StreamListener(dispatcher, screen_name)).userstream()
        print('[StreamListener] disconnected!')


try:
    auth_data = json.load(open('twitterauth.data', 'r'))
except FileNotFoundError:
    print('I need authorisation!')
    print('Please register an app!')
    # noinspection PyDictCreation
    auth_data = {}
    auth_data['consumer_key'] = input('consumer_key >>> ').strip()
    auth_data['consumer_secret'] = input('consumer_secret >>> ').strip()
    auth = tweepy.OAuthHandler(auth_data['consumer_key'], auth_data['consumer_secret'])
    print('You can now authenticate here:', auth.get_authorization_url(access_type='read-write'))
    verifier = input('verifier >>> ').strip()
    auth.get_access_token(verifier)
    auth_data['access_token'] = auth.access_token
    auth_data['access_token_secret'] = auth.access_token_secret
    print('Done! Thanks! Saved to twitterauth.data.')
    twitter_api = tweepy.API(auth)
    auth_data['screen_name'] = twitter_api.me().screen_name
    json.dump(auth_data, open('twitterauth.data', 'w'))
    print('Done! Logged in as @%s! Login data saved to twitterauth.data' % auth_data['screen_name'])
else:
    auth = tweepy.OAuthHandler(auth_data['consumer_key'], auth_data['consumer_secret'])
    auth.set_access_token(auth_data['access_token'], auth_data['access_token_secret'])
    twitter_api = tweepy.API(auth)

tweet_dispatcher = TweetDispatcher(twitter_api)
thread = Thread(target=tweet_dispatcher.run, daemon=True)
thread.start()

thread = Thread(target=start_stream, args=(auth, tweet_dispatcher, auth_data['screen_name']))
thread.start()
