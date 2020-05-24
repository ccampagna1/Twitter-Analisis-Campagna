from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import twitter_credentials
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

import json
import os


####### TWITTER CLIENT ########
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    # Mediante la clase Cursor podemos obtener los tweets de una cuenta de usuario
    # Pasamos por parametro las cantidades de tweets que queremos de ese usuario particular
    def get_user_timeline_tweets(self, num_tweets, lang):
        tweets = []

        # Si no damos un usuario al metodo Cursor nos devolvera los tweets de nuestra propia linea de tiempo
        # Para que no nos devuelva toda la historia de tweets, ponemos un limite de tweets a devolver
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user, lang=lang).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends).items(num_friends):
            friend_list.append(friend)
        return friend_list

    # Tweets que retweetias, compartis e inclusive los propios
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


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
    # twitter_client = TwitterClient()
    # tweet_analyzer = TweetAnalyzer()

    # api = twitter_client.get_twitter_client_api()

    # es una funcion provenida desde la libreria API creada en el "twitter client"
    # nos permite especificar usuario, cuantos tweets sacar de ese usuario
    # tweets = api.user_timeline(screen_name="realdonaldtrump", count=50, lang='en')

    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    # print(df.head(10))

    #    CLASE 1 - STREAMING DE TWEETS

    hash_tag_list = ['aerolineas argentinas', 'clima']
    fetched_tweets_filename = "df_tweets.csv"

    #    interested_columns = ['Tweets', 'User', 'User_statuses_count',
    #                             'user_followers', 'User_location', 'User_verified',
    #                             'fav_count', 'rt_count', 'tweet_date']
    #
    #    tweet_analyzer = TweetAnalyzer(interested_columns)

    twetter_streamer = TwitterStreamer()
    twetter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

# %%    CLASE 2 - CURSOR Y PAGINACION

# =============================================================================
#     # Con esto podemos ver cuales son los campos que podemos consultar de un tweet.
#     #print(dir(tweets[0]))
#    
#     twitter_client = TwitterClient('pycon')
#     print(twitter_client.get_user_timeline_tweets(1))
#    
#     # cuenta la cantidad de retweets que tuvo un tweet
#     #print(tweets[0].retweet_count)
# =============================================================================

# %%    CLASE 3 - ANALISIS DE LOS DATOS

# =============================================================================
#     # Get average length over all tweets.
#     print(np.mean(df['len']))
#     
#     # Get the number of likes for the most liked tweet.
#     print(np.max(df['likes']))
#     
#     # Get the number of retweets for the most retweeted tweet.
#     print(np.max(df['retweets']))
# =============================================================================

# %%    CLASE 4 - VISUALIZACION DE LA INFORMACION

# =============================================================================
#     #Time Series
#     time_likes = pd.Series(data=df['likes'].values, index=df['date'])
#     time_likes.plot(figsize = (16,4),color = 'r')
#     plt.show()
#     
#     time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
#     time_retweets.plot(figsize = (16,4), color = 'b')
#     plt.show()
#     
#     time_likes = pd.Series(data=df['likes'].values, index=df['date'])
#     time_likes.plot(figsize = (16,4), label = 'Likes', legend = True)
# 
#     time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
#     time_retweets.plot(figsize = (16,4), label = 'retweets', legend = True)
#     plt.show()
# =============================================================================

# %%    CLASE 5 ANALISIS DE SENTIMIENTOS

# =============================================================================
#    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
#    
#    print(df.head(10))
#
# =============================================================================
