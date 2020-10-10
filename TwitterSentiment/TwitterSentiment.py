#!/usr/bin/env python
# coding: utf-8

import json
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from textblob import TextBlob
import tweepy
from tweepy import OAuthHandler
import datetime

now = datetime.datetime.now()
consumer_key = "*****"
consumer_secret = "*****"
access_token = "*****"
access_token_secret = "*****"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

def remove_url(txt):
    """Replace URLs found in a text string with nothing 
    (i.e. it will remove the URL from the string).

    Parameters
    ----------
    txt : string
        A text string that you want to parse and remove urls.

    Returns
    -------
    The same txt string with url's removed.
    """

    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

def determine_sentiment(tweet):
    if tweet.sentiment.polarity < 0:
        sentiment = "negative"
    elif tweet.sentiment.polarity == 0:
        sentiment = "neutral"
    else:
        sentiment = "positive"
    return sentiment

def get_tweets(search_term, items = 1000, incl_retweets = False):
    """Uses the tweepy api to get tweets

    Parameters
    ----------
    search_term (string)
        The hashtag that you want to search Twitter for
    items (int)
        The amount of tweets to return, if available. Max set to 1000
    incl_retweets (boolean)
        Whether or not to include retweets

    Returns
    -------
    Returns an object of tweets
    """
    
    pd.reset_option('^display.', silent=True)
    
    # Clean input
    search_term = search_term.strip()
    
    if len(search_term.split()) > 1:
        search_term = search_term.replace(' ','+')
        
    if items > 1000:
        items = 1000
        print('Using max items of 1000.')

    if incl_retweets:
        q_string = '#' + search_term
    else:
        q_string = '#' + search_term + ' -filter:retweets'
        
    tweets = tweepy.Cursor(api.search,
                           q=search_term,
                           lang="en",
                           since=str(now.year)+'-01-01').items(items)
    
    return tweets

def create_tweet_df(tweets):
    
    # Remove URLs
    tweets = [remove_url(tweet.text) for tweet in tweets]

    # Create textblob objects of the tweets
    sentiment_objects = [TextBlob(tweet) for tweet in tweets]

    # Create list of polarity values and tweet text
    sentiment_values = [[tweet.sentiment.polarity, determine_sentiment(tweet), str(tweet)] for tweet in sentiment_objects]

    # Create dataframe containing the polarity value and tweet text
    sentiment_df = pd.DataFrame(sentiment_values, columns = ["polarity", "sentiment", "tweet"])
    sentiment_df = sentiment_df[sentiment_df['polarity'] != 0].reset_index(drop=True)
    sentiment_df.drop_duplicates(inplace = True)
    
    return sentiment_df

def plot_tweet_sentiment(sentiment_df):
    
    sns.set_style(style="darkgrid")
    sns.distplot(sentiment_df['polarity'], kde = False)
    plt.axvline(sentiment_df['polarity'].mean(), 0, 50, c='black')
    plt.text(sentiment_df['polarity'].mean()+0.02,1,round(sentiment_df['polarity'].mean(),2))
    plt.show()

def get_top_tweets(sentiment_df, top=True, amount=10):
    
    pd.set_option('display.max_colwidth', -1, silent = True)
    
    if top:
        return sentiment_df.sort_values('polarity')[:amount]['tweet']
    else:
        return sentiment_df.sort_values('polarity', ascending=False)[:amount]['tweet']

def clean_input(user_string):
    
    if user_string == '':
        return user_string
    else:
        return re.sub('[\W_]+', '', user_string.split()[0]).lower()

if __name__ == '__main__':
    
    while True:
    
        while True:

            kw = input('Please enter a single keyword to search on Twitter. If multiple words are entered, only the first will be used. ')
            kw = clean_input(kw)
            if kw == '':
                print('Invalid input. Please enter at least 1 alphanumeric string.')
                continue
            else:
                break

        while True:

            rt = input('Would you like to include retweets in the search? Please enter yes/no. ')
            if rt == '' or rt.lower()[0] not in ['y','n']:
                print("Invalid input. Please enter 'yes' or 'no'. ")
                continue
            else:
                break

        rt = (rt.lower()[0] == 'y')

        print('Compiling tweets...')
        tweets = get_tweets(kw, incl_retweets = rt)
        df = create_tweet_df(tweets)

        print('Done! Here are some results.')
        print(df.head(5))

        print('Here is a plot of the sentiment.')
        plot_tweet_sentiment(df)

        while True:

            see_top = input('Would you like to see the top most negative or positive tweets? Please enter yes/no. ')
            if see_top == '' or see_top.lower()[0] not in ['y','n']:
                print("Invalid input. Please enter 'yes' or 'no'. ")
                continue
            else:
                break

        see_top = (see_top.lower()[0] == 'y')

        if see_top:

            while True:

                top_bot = input('Would you like to see the positive or negative tweets? Please enter positive/negative. ')
                if top_bot == '' or top_bot.lower()[0] not in ['p','n']:
                    print("Invalid input. Please enter 'positive' or 'negative'. ")
                    continue
                else:
                    break

            while True:

                try:
                    top_bot_num = int(input('How many tweets would you like to see? Please enter an integer between 1 and 25. '))
                except ValueError:
                    print('Number not entered. Please try again. ')
                else:
                    break

            if top_bot_num > 25:
                print('Number greater than 25 was input. Using 25 instead.')
                top_bot_num = 25
                
            if top_bot_num < 1:
                print('Negative number entered. Using 5 instead.')
                top_bot_num = 5

            top_bot = (top_bot.lower()[0] == 'n')

            print('Here are your results.')
            print(get_top_tweets(df, top = top_bot,amount = top_bot_num))
        else:
            print('Okay. See ya!')
            break

        while True:
            
            cont = input('Would you like to try a new keyword? ')
            if cont == '' or cont.lower()[0] not in ['y','n']:
                print("Invalid input. Please enter 'yes' or 'no'. ")
                continue
            else:
                break
                
        cont = (cont.lower()[0] == 'y')
        
        if cont:
            continue
        else:
            print('Okay. See ya!')
            break
