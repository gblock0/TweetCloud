import os
from typing import List, Optional

import twitter
from alive_progress import alive_bar
from twitter import Status

_session = None


def _twitter_api_session() -> twitter.Api:
    """
    Create new Twitter API session, or get cached session if available.
    """
    global _session
    if _session is None:
        _session = twitter.Api(
            consumer_key=os.getenv("TWTR_CONS_KEY"),
            consumer_secret=os.getenv("TWTR_CONS_SEC"),
            access_token_key=os.getenv("TWTR_ACC_KEY"),
            access_token_secret=os.getenv("TWTR_ACC_SEC"),
            tweet_mode="extended",
        )
    return _session


def get_latest_tweets(screen_name: str, number_of_tweets: int) -> List[Status]:
    """
    Get the specified number of tweets for `screen_name`.
    """
    session = _twitter_api_session()

    with alive_bar(
        total=number_of_tweets,
        title="Downloading tweets",
        spinner="dots_reverse",
        manual=True,
    ) as bar:
        last_id: Optional[int] = None
        tweets: List[Status] = []

        while len(tweets) < number_of_tweets:
            new_tweets: List[Status] = session.GetUserTimeline(
                screen_name=screen_name,
                # without setting this, only a few tweets will
                # be returned on each query.
                count=min(number_of_tweets, 200),
                max_id=last_id,
                include_rts=False,
            )

            if new_tweets:
                tweets.extend(new_tweets[: (number_of_tweets - len(tweets))])
                bar(len(tweets) / number_of_tweets)
                last_id = new_tweets[-1].id - 1

            else:
                break

    return tweets
