import os
import tempfile

import click
import twitter

from tweetcloud.helpers import text as texthelper
from tweetcloud.helpers import twitter_api
from tweetcloud.visualization import wordcloud


@click.command()
@click.option("-n", "--number-of-tweets", type=click.IntRange(0, 3000), default=1000)
@click.argument("screen_name", type=click.STRING)
def cli(screen_name: str, number_of_tweets: int):
    # Connect to the Twitter API
    session = twitter.Api(
        consumer_key=os.getenv("TWTR_CONS_KEY"),
        consumer_secret=os.getenv("TWTR_CONS_SEC"),
        access_token_key=os.getenv("TWTR_ACC_KEY"),
        access_token_secret=os.getenv("TWTR_ACC_SEC"),
        tweet_mode="extended",
    )

    # Get all the tweets for the user
    all_tweets = twitter_api.get_all_tweets(session, screen_name, number_of_tweets)

    # Normalize all the tweets and add the words to the words_of_the_weeks dictionary
    words_of_the_weeks = texthelper.transform_tweets_to_word_counts(all_tweets)

    with tempfile.TemporaryDirectory(prefix="tweetcloud-") as tmpdir:
        word_clouds = []
        sorted_dates = sorted(words_of_the_weeks)
        start_date = sorted_dates[0]
        end_date = sorted_dates[-1]
        for date in sorted_dates:
            word_clouds.append(
                wordcloud.create_wordcloud(
                    words_of_the_weeks[date], date, tmpdir, screen_name
                )
            )

        word_clouds[0].save(
            f"{screen_name}-{start_date:%Y-%m-%d}-to-{end_date:%Y-%m-%d}.gif",
            save_all=True,
            append_images=word_clouds[1:],
            optimized=False,
            duration=3000,
            loop=0,
        )
