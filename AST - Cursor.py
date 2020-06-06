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


def process_tweet(tweet, i):
    df = pd.DataFrame(columns=['Tweets', 'Tweets_retweet', 'User', 'User_statuses_count',
                               'user_followers', 'User_location', 'User_verified',
                               'fav_count', 'rt_count', 'tweet_date'])
    df.loc[i, 'Tweets'] = tweet.full_text
    if 'retweeted_status' in dir(tweet):
        df.loc[i, 'retweeted_status'] = tweet.retweeted_status.full_text
    else:
        df.loc[i, 'retweeted_status'] = tweet.full_text
    df.loc[i, 'User'] = tweet.user.name
    df.loc[i, 'User_statuses_count'] = tweet.user.statuses_count
    df.loc[i, 'user_followers'] = tweet.user.followers_count
    df.loc[i, 'User_location'] = tweet.user.location
    df.loc[i, 'User_verified'] = tweet.user.verified
    df.loc[i, 'fav_count'] = tweet.favorite_count
    df.loc[i, 'rt_count'] = tweet.retweet_count
    df.loc[i, 'tweet_date'] = tweet.created_at
    return df


def capture_tweets(corpus, fetched_tweets_filename, count, tweepy):
    # if os.path.isfile(fetched_tweets_filename):
    #     df_tweets = pd.read_excel(fetched_tweets_filename)
    # else:
    df_tweets = pd.DataFrame(columns=['Tweets', 'User', 'User_statuses_count',
                                      'user_followers', 'User_location', 'User_verified',
                                      'fav_count', 'rt_count', 'tweet_date'])
    i = 0

    for tweet in Cursor(tweepy.search, q=corpus, tweet_mode='extended').items(count):  # , lang='es'
        print(i, end='\r')  # Para ver por que tweet voy agregando
        df_tweets = df_tweets.append(process_tweet(tweet, i))
        i += 1

    df_tweets.head()
    df_tweets.to_excel(fetched_tweets_filename)


# Proceso Principal
if __name__ == "__main__":
    hash_tag_list = ['aerolineas argentinas', 'clima']
    fetched_tweets_filename = "tweets_arsa_crudo_prueba.xlsx"

    # Palabras claves a aparecer en los tweets
    corpus = ['aerolineas argentinas']
    count = 10

    twitter_client = TwitterClient()
    tweepy = twitter_client.get_twitter_client_api()

    capture_tweets(corpus, fetched_tweets_filename, count, tweepy)

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
