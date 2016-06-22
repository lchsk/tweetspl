#! -*- encoding: utf-8 -*-
import json
import os

import tweepy

from tweepy import (
    OAuthHandler,
    Stream,
)

from tweepy.streaming import StreamListener

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_secret = os.getenv('ACCESS_SECRET')

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

keywords = [
    u'pogoda', u'polityka', u'euro', u'polska', u'piłka', u'prezydent', u'sejm',
    u'jutro', u'zdjęcie', u'wczoraj', u'gra'
]

class TweetListener(StreamListener):
    def on_data(self, data):
        try:
            with open('../data/tweets.raw', 'a') as f:
                tweet = json.loads(data)

                if tweet['lang'] == 'pl':
                    text = tweet['text'].encode(
                        'utf-8'
                    ).replace(
                        '\n', ''
                    ).replace(
                        '\t', ''
                    )

                    print text

                    f.write('{0}\n'.format(text))

        except BaseException as e:
            print("Error on_data: %s" % str(e))

    def on_error(self, status):
        print(status)
        return True

twitter_stream = Stream(auth, TweetListener())
twitter_stream.filter(track=keywords, async=False)
