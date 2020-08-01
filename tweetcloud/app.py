import argparse
import logging
import os
import shutil
from datetime import datetime, timedelta

import coloredlogs
import twitter
from PIL import Image

from tweetcloud import helpers


def main():

    parser = argparse.ArgumentParser(
        description="Gets a dictionary of the most used words per week from an account"
    )
    parser.add_argument("screen_name", help="screen name to map")
    parser.add_argument(
        "number_of_tweets", type=int, help="number of tweets to grab from Twitter"
    )

    args = parser.parse_args()

    if args.number_of_tweets > 3000:
        coloredlogs.install()
        logging.warning(
            "TweetCloud does not currently support getting more than 3000 tweets, "
            "so only 3000 tweets will be used for your gif..."
        )

    # Create the temp folder for the images
    tmp_image_folder = "tmpPhotos"

    # Create folder for intermediate images
    if not os.path.isdir(tmp_image_folder):
        os.mkdir(tmp_image_folder)

    # Connect to the Twitter API
    t = twitter.Api(
        consumer_key=os.environ.get("TWTR_CONS_KEY"),
        consumer_secret=os.environ.get("TWTR_CONS_SEC"),
        access_token_key=os.environ.get("TWTR_ACC_KEY"),
        access_token_secret=os.environ.get("TWTR_ACC_SEC"),
        tweet_mode="extended",
    )

    # Get all the tweets for the user
    all_tweets = helpers.get_all_tweets(t, args.screen_name, args.number_of_tweets)

    words_of_the_weeks = {}

    # Normalize all the tweets and add the words to the words_of_the_weeks dictionary
    for tweet in all_tweets:
        date_of_tweet = datetime.strptime(
            tweet.created_at, "%a %b %d %H:%M:%S %z %Y"
        ).date()
        sunday_of_tweet = date_of_tweet - timedelta(days=date_of_tweet.weekday() + 1)

        if sunday_of_tweet not in words_of_the_weeks:
            words_of_the_weeks[sunday_of_tweet] = {}

        current_words = words_of_the_weeks[sunday_of_tweet]
        helpers.normalize_and_split_tweet(tweet.full_text, current_words)

    word_clouds = []
    sorted_dates = sorted(words_of_the_weeks.keys())
    start_date = sorted_dates[0]
    end_date = sorted_dates[-1]
    for date in sorted_dates:
        word_clouds.append(
            Image.open(
                helpers.create_wordcloud(
                    words_of_the_weeks[date], date, tmp_image_folder, args.screen_name
                )
            )
        )

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
