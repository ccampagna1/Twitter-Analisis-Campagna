from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import twitter_credentials
import pandas as pd
import re

import json
import os


####### TWITTER AUTHENTICATER ########
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token_key, twitter_credentials.access_token_secret)
        return auth


####### TWITTER STREAMER ########
class TwitterStreamer():
    """
    Esta clase es para stremear y procesar tweets en vivo
    """

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # maneja la autentificacion y la coneccion con la API de streaming de twitter. Metodo preveniente de la clase
        # Stream
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # Filtra los twitters por los hashtags que sean pasados:
        stream.filter(track=hash_tag_list)


####### TWITTER STREAM LISTENER ########
class TwitterListener(StreamListener):
    """
    Listener basico que imprime los tweets que recive. Vamos a construir
    una clase que nos permita imprimir los tweets que van llegando.
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    # estamos sobreescribiendo los metodos de la clase streamListener
    def on_data(self, data):

        ta = TweetAnalyzer()

        try:
            tweet = json.loads(data)

            if os.path.isfile(self.fetched_tweets_filename):
                df_tweets = pd.read_csv(self.fetched_tweets_filename)
            else:
                df_tweets = pd.DataFrame()

            ta.tweet_to_data_frame(tweet, self.fetched_tweets_filename, df_tweets)

        except BaseException as e:
            print("Error on_data: %s" % str(e))

        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


####### TWITTER ANALYZER ########
class TweetAnalyzer():
    """
    Analizar y categorizar el contenido de los tweets.
    """

    def __init__(self):
        pass

    def tweet_to_data_frame(self, tweet, fetched_tweets_filename, df):

        i = df.shape[0]

        df.loc[i, 'tweets'] = tweet['text']
        df.loc[i, 'user'] = tweet['user']['name']
        df.loc[i, 'user_statuses_count'] = tweet['user']['statuses_count']
        df.loc[i, 'user_followers'] = tweet['user']['followers_count']
        df.loc[i, 'user_location'] = tweet['user']['location']
        df.loc[i, 'user_verified'] = tweet['user']['verified']
        df.loc[i, 'fav_count'] = tweet['favorite_count']
        df.loc[i, 'rt_count'] = tweet['retweet_count']
        df.loc[i, 'tweet_date'] = tweet['created_at']
        df.loc[i, 'sentiment'] = self.analyze_sentiment(tweet['text'])

        # if tweet['retweeted_status']:
        #     df['Tweets_retweet'] = tweet['retweeted_status']['extended_tweet']["full_text"]
        # else:
        #     df['Tweets_retweet'] = ''

        df.to_csv(fetched_tweets_filename, index=False)

    def clean_tweet(self, tweet):
        # expresion regular que elimina caracteres especiaey links. Mantiene solo
        # valores alfanumericos y elimina cadenas que tienen las barras dentro de una "palabra"
        clean_tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        # print(clean_tweet)
        return clean_tweet

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        # si es positivo se interpreta que el tweet es positivo
        if analysis.sentiment.polarity > 0:
            return 1

        if analysis.sentiment.polarity == 0:
            return 0

        if analysis.sentiment.polarity < 0:
            return -1


# Proceso Principal
if __name__ == "__main__":

    hash_tag_list = ['aerolineas argentinas', 'clima']
    fetched_tweets_filename = "df_tweets.csv"

    twetter_streamer = TwitterStreamer()
    twetter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

