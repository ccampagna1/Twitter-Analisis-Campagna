from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler

from textblob import TextBlob

import twitter_credentials
import pandas as pd
import re
# import matplotlib.pyplot as plt

import json
import os


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


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token_key, twitter_credentials.access_token_secret)
        return auth


def clean_tweet(tweet):
    # expresion regular que elimina caracteres especiaey links. Mantiene solo
    # valores alfanumericos y elimina cadenas que tienen las barras dentro de una "palabra"
    # clean_tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    # print(clean_tweet)
    return clean_tweet


def analyze_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))

    # si es positivo se interpreta que el tweet es positivo
    if analysis.sentiment.polarity > 0:
        return 1

    if analysis.sentiment.polarity == 0:
        return 0

    if analysis.sentiment.polarity < 0:
        return -1


def process_tweet(tweet):
    """
    Se campura la informacion requerida de un tweet.
    """

    data_tweet = {'tweet_id': tweet.id, 'tweet_full_text': '', 'tweet_fav_count': tweet.favorite_count,
                  'tweet_retweet_count': tweet.retweet_count,
                  'tweet_source': tweet.source, 'tweet_date': tweet.created_at, 'tweet_hashtags': tweet.entities['hashtags'],
                  'user_id': tweet.user.id, 'user_name': tweet.user.name, 'user_screen_name': tweet.user.screen_name,
                  'user_description': tweet.user.description, 'user_statuses_count': tweet.user.statuses_count,
                  'user_favourites_count': tweet.user.favourites_count, 'user_followers': tweet.user.followers_count,
                  'user_friends': tweet.user.friends_count, 'user_verified': tweet.user.verified,
                  'user_location': tweet.user.location, 'user_date': tweet.user.created_at}

    if 'retweeted_status' in dir(tweet):
        data_tweet['tweet_full_text'] = tweet.retweeted_status.full_text
    else:
        data_tweet['tweet_full_text'] = tweet.full_text

    return data_tweet


def capture_tweets(corpus, fetched_tweets_filename, count, tweepy):
    i = 0
    if os.path.isfile(fetched_tweets_filename):
        df_tweets = pd.read_excel(fetched_tweets_filename)
    else:
        df_tweets = pd.DataFrame()

    for tweet in Cursor(tweepy.search, q=corpus, tweet_mode='extended').items(count):  # , lang='es'
        print(i, end='\r')
        df_tweets = df_tweets.append(process_tweet(tweet), ignore_index=True)
        i += 1

    df_tweets.to_excel(fetched_tweets_filename, index=False)


# Proceso Principal
if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweepy = twitter_client.get_twitter_client_api()

    # Palabras claves a aparecer en los tweets ,
    word_tag_lists = [['aerolineas', 'argentinas', 'austral'],
                      ['aerolineas', 'argentinas', 'vuelos'],
                      ['aerolineas', 'argentinas', 'paro'],
                      ['aerolineas', 'argentinas', 'gremio']]

    # Cantidad de tweets a traer
    count = 100000

    # Nombre del archivo donde se almacenaran los tweets
    fetched_tweets_filename = "tweets_arsa_crudo.xlsx"

    for wtl in word_tag_lists:
        capture_tweets(wtl, fetched_tweets_filename, count, tweepy)

# %% Modulo comentado

# es una funcion provenida desde la libreria API creada en el "twitter client"
# nos permite especificar usuario, cuantos tweets sacar de ese usuario
# tweets = api.user_timeline(screen_name="realdonaldtrump", count=50, lang='en')

# df = tweet_analyzer.tweets_to_data_frame(tweets)
# print(df.head(10))


#    interested_columns = ['Tweets', 'User', 'User_statuses_count',
#                             'user_followers', 'User_location', 'User_verified',
#                             'fav_count', 'rt_count', 'tweet_date']
#
#    tweet_analyzer = TweetAnalyzer(interested_columns)


# %% ANALISIS DE LOS DATOS

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

# %% VISUALIZACION DE LA INFORMACION

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
