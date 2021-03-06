import click

from tweetcloud.helpers import text as texthelper
from tweetcloud.helpers import twitter_api
from tweetcloud.visualization import wordcloud

MAX_TWEETS = 3000


@click.command()
@click.option(
    "-n",
    "--number-of-tweets",
    type=click.IntRange(0, MAX_TWEETS),
    default=1000,
    show_default=True,
    metavar="",
    help=(
        f"Number of tweets to use in total. Currently, TweetCloud "
        f"does not support more than {MAX_TWEETS} tweets."
        f"\n\nNote that the tweets are grouped by time, not count, so "
        f"using this option may not affect the frames in the GIF."
    ),
)
@click.argument("screen_name", type=click.STRING)
def cli(screen_name: str, number_of_tweets: int):
    """
    Generate animated series of word clouds from SCREEN_NAME's tweets.

    Example: tweetcloud nasa
    """
    # Get all the tweets for the user
    all_tweets = twitter_api.get_latest_tweets(screen_name, number_of_tweets)

    # Normalize all the tweets and add the words to the words_of_the_weeks dictionary
    words_of_the_weeks = texthelper.transform_tweets_to_word_counts(all_tweets)
    filename = wordcloud.create_animation(
        word_counts=words_of_the_weeks, screen_name=screen_name
    )
    click.echo(f"Animation saved to {filename}")
