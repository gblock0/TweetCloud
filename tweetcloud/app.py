import argparse
import html
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from math import ceil

import coloredlogs
import matplotlib.pyplot as plt
import twitter
from PIL import Image
from wordcloud import STOPWORDS, WordCloud

parser = argparse.ArgumentParser(
    description="Gets a dictionary of the most used words per week from an account"
)
parser.add_argument("screen_name", help="screen name to map")
parser.add_argument(
    "number_of_tweets", type=int, help="number of tweets to grab from Twitter"
)

args = parser.parse_args()

# Create the temp folder for the images
tmp_image_folder = "tmpPhotos"

# Connect to the Twitter API
t = twitter.Api(
    consumer_key=os.environ.get("TWTR_CONS_KEY"),
    consumer_secret=os.environ.get("TWTR_CONS_SEC"),
    access_token_key=os.environ.get("TWTR_ACC_KEY"),
    access_token_secret=os.environ.get("TWTR_ACC_SEC"),
    tweet_mode="extended",
)

# Stop Words
stop_words = {'go', "will"}.union(set(STOPWORDS))
words_of_the_weeks = {}
MAX_COUNT_FROM_TWITTER = 200


# Normalize the tweet:
#   - Remove mentions, emails, and websites
#   - Disregard retweeted tweets
def normalize_and_add_to_words(tweet):
    full_text = html.unescape(tweet.full_text)
    date_of_tweet = datetime.strptime(
        tweet.created_at, "%a %b %d %H:%M:%S %z %Y"
    ).date()
    sunday_of_tweet = date_of_tweet - timedelta(days=date_of_tweet.weekday() + 1)
    match_rt = full_text.startswith("RT @")

    # Remove mentions
    normalized_full_text = re.sub(r"(\A){0,1}@[\d\w]*(\s|\Z){1}", "", full_text)

    # Remove emails
    normalized_full_text = re.sub(
        r"(\A){0,1}[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}(\s|\Z){1}",
        "",
        normalized_full_text,
    )

    # Only look at words that weren't in retweeted tweets and are more than 1 character
    if not match_rt and len(normalized_full_text) > 0:
        if sunday_of_tweet not in words_of_the_weeks:
            words_of_the_weeks[sunday_of_tweet] = {}

        words = words_of_the_weeks[sunday_of_tweet]
        words_in_tweet = normalized_full_text.split()
        for word in words_in_tweet:
            match_website = re.search("^http[s]?://", word)
            normalized_word = re.sub(r"[\W\d]+", "", word.lower())
            if (
                normalized_word not in stop_words
                and len(normalized_word) > 1
                and not match_website
            ):
                if normalized_word in words_of_the_weeks[sunday_of_tweet]:
                    words[normalized_word] += +1
                else:
                    words[normalized_word] = 1


# Gets the number tweets for a screen_name specified in the command line args
def get_all_tweets(screen_name):
    count = MAX_COUNT_FROM_TWITTER
    number_of_extra_api_calls = 0
    if args.number_of_tweets < MAX_COUNT_FROM_TWITTER:
        count = args.number_of_tweets
    elif args.number_of_tweets > MAX_COUNT_FROM_TWITTER:
        number_of_extra_api_calls = ceil(
            (args.number_of_tweets - MAX_COUNT_FROM_TWITTER) / MAX_COUNT_FROM_TWITTER
        )
    all_tweets = t.GetUserTimeline(
        screen_name=screen_name, count=count, include_rts=False
    )
    last_id = all_tweets[-1].id
    number_of_tweets_to_find = args.number_of_tweets - count

    for _ in range(number_of_extra_api_calls):
        if number_of_tweets_to_find < MAX_COUNT_FROM_TWITTER:
            count = number_of_tweets_to_find

        new = t.GetUserTimeline(
            screen_name=screen_name, count=count, max_id=last_id - 1, include_rts=False
        )
        number_of_tweets_to_find -= count

        if len(new) > 0:
            all_tweets.extend(new)
            last_id = new[-1].id
        else:
            break

    return all_tweets


# Creates a word cloud from the passed in word/frequency dictionary
# and saved it in tmp_image_folder
def create_wordcloud(words, date):
    wordcloud = WordCloud(
        width=950, height=950, background_color="white", min_font_size=10
    ).generate_from_frequencies(words)
    plt.figure(figsize=(9.5, 10), facecolor=None)
    plt.title(
        "Words seen the week of " + str(date) + " in " + args.screen_name + "'s tweets",
        {"fontsize": 18, "fontweight": 600},
        pad=20,
    )
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.imshow(wordcloud)
    file_path = tmp_image_folder + "/image-" + str(date) + ".png"
    plt.savefig(file_path)
    return Image.open(file_path)


def main():
    if args.number_of_tweets > 3000:
        coloredlogs.install()
        logging.warning(
            "TweetCloud does not currently support getting more than 3000 tweets, "
            "so only 3000 tweets will be used for your gif..."
        )

    # Create folder for intermediate images
    if not os.path.isdir(tmp_image_folder):
        os.mkdir(tmp_image_folder)

    # Get all the tweets for the user
    all_tweets = get_all_tweets(args.screen_name)

    # Normalize all the tweets and add the words to the words_of_the_weeks dictionary
    for tweet in all_tweets:
        normalize_and_add_to_words(tweet)

    word_clouds = []
    sorted_dates = sorted(words_of_the_weeks.keys())
    start_date = sorted_dates[0]
    end_date = sorted_dates[-1]
    for date in sorted_dates:
        word_clouds.append(create_wordcloud(words_of_the_weeks[date], date))

    word_clouds[0].save(
        args.screen_name + "-" + str(start_date) + "-to-" + str(end_date) + ".gif",
        save_all=True,
        append_images=word_clouds[1:],
        optimized=False,
        duration=3000,
        loop=0,
    )

    # Cleanup intermediate images
    shutil.rmtree(tmp_image_folder)


if __name__ == "__main__":
    main()
