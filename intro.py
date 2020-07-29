import requests
import html
import twitter
import re
import os
import argparse
from math import ceil
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='Gets a dictionary of the most used words per week from an account')
parser.add_argument('screen_name', help='screen name to map')
parser.add_argument('number_of_tweets', type=int, help='number of tweets to grab from Twitter')

args = parser.parse_args()

# Connect to the Twitter API
t = twitter.Api(
    consumer_key = os.environ.get('TWTR_CONS_KEY'),
    consumer_secret = os.environ.get('TWTR_CONS_SEC'),
    access_token_key = os.environ.get('TWTR_ACC_KEY'),
    access_token_secret = os.environ.get('TWTR_ACC_SEC'),
    tweet_mode = 'extended'
)

# Common words we don't care to keep track of
common_words = {'the', 'or', 'a', 'an', 'this', 'on', 'it', 'are',
                'to', 'out', 'and','as', 'of', 'so', 'for', 'be',
                'in', 'that', 'we', 'at','is', 'were','if','i',
                'do', 'he', 'with', 'have', 'by', 'am'
                }
words_of_week = {}
MAX_COUNT_FROM_TWITTER = 200

# Normalize the tweet:
#   - Remove mentions, emails, and websites
#   - Disregard retweeted tweets
def normalize_tweet(tweet):
    full_text = html.unescape(tweet.full_text)
    date_of_tweet = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y').date()
    sunday_of_tweet = date_of_tweet - timedelta(days=date_of_tweet.weekday() +1)
    match_rt = full_text.startswith('RT @')

    # Remove mentions
    normalized_full_text = re.sub('(\A){0,1}@[\d\w]*(\s|\Z){1}', '', full_text)

    # Remove emails
    normalized_full_text = re.sub('(\A){0,1}[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}(\s|\Z){1}','', normalized_full_text)

    # Only look at words that weren't in retweeted tweets and are more than 1 character
    if (not match_rt and len(normalized_full_text) > 0):
        if sunday_of_tweet not in words_of_week:
            words_of_week[sunday_of_tweet] = {}

        words = words_of_week[sunday_of_tweet]
        words_in_tweet = normalized_full_text.split()
        for word in words_in_tweet:
            match_website = re.search('^http[s]?://', word)
            normalized_word = re.sub(r'[\W\d]+','', word.lower())
            if normalized_word not in common_words and len(normalized_word) > 1 and not match_website:
                if normalized_word in words_of_week[sunday_of_tweet]:
                    words[normalized_word] = words[normalized_word] + 1
                else:
                    words[normalized_word] = 1

def get_all_tweets(screen_name):
    count = MAX_COUNT_FROM_TWITTER
    number_of_api_calls = 0
    if args.number_of_tweets < MAX_COUNT_FROM_TWITTER:
        count = args.number_of_tweets
    elif args.number_of_tweets > MAX_COUNT_FROM_TWITTER:
        number_of_api_calls = ceil((args.number_of_tweets - MAX_COUNT_FROM_TWITTER)/MAX_COUNT_FROM_TWITTER)
    all_tweets = t.GetUserTimeline(screen_name=screen_name, count=count)
    last_id = all_tweets[-1].id
    for i in range(number_of_api_calls):
        new = t.GetUserTimeline(screen_name=screen_name, max_id=last_id-1)
        if len(new) > 0:
            all_tweets.extend(new)
            last_id = new[-1].id
        else:
            break

    return all_tweets

all_tweets = get_all_tweets(args.screen_name)

for tweet in all_tweets:
    normalize_tweet(tweet)

# Print out the words and their counts for each week
for week in words_of_week:
    print(week)
    words = words_of_week[week]
    sorted_items = sorted(words.items(), key=lambda x:x[1])

    for item in sorted_items:
        if item[1] > 1:
            print(item[0], item[1])
