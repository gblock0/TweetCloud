import collections
import datetime
import html
import re
from itertools import groupby
from typing import Counter, Dict, Final, Iterable, Optional

from twitter import Status
from wordcloud import STOPWORDS

stop_words: Final = {"go", "will"}.union(set(STOPWORDS))
URL_PATTERN: Final = re.compile(r"https?://")
EMAIL_PATTERN: Final = re.compile(r"[\w.\-+%]+@[\w.\-]+\.[a-zA-Z]{2,}")
MENTIONS_PATTERN: Final = re.compile(r"@\w+")
stop_patterns: Final = (URL_PATTERN, MENTIONS_PATTERN, EMAIL_PATTERN)
BAD_CHAR_PATTERN: Final = re.compile(r"[\W\d]+")


def transform_tweets_to_word_counts(
    tweets: Iterable[Status],
) -> Dict[datetime.date, Counter[str]]:
    """
    Group tweets and return normalized word counts per group.
    """
    groups = groupby(sorted(tweets, key=_tweet_group_key), key=_tweet_group_key)
    # Lots of iteration here. If we start processing tons of tweets
    # it might be noticeable, but if it comes to that we should use
    # a proper text processing library.
    return {
        key: sum(map(normalize_and_split_tweet, group), start=collections.Counter())
        for key, group in groups
    }


def _tweet_group_key(tweet: Status) -> datetime.date:
    """
    Get the grouping key for each tweet, i.e., the Monday prior to the
    tweet's date.
    """
    tweet_date = datetime.datetime.utcfromtimestamp(tweet.created_at_in_seconds)
    weekstart = *tweet_date.isocalendar()[:2], 1
    return datetime.date.fromisocalendar(*weekstart)


def normalize_and_split_tweet(tweet: Status) -> Counter[str]:
    """
    Convert a tweet's text into normalized term counts.
    """
    raw_text: Final[str] = tweet.full_text

    if not raw_text:
        return collections.Counter()

    text: Final = html.unescape(raw_text).casefold()
    # Only look at words that weren't in retweeted tweets
    if text.startswith("rt @"):
        return collections.Counter()

    # filter out `None`s
    return collections.Counter(filter(None, map(_normalize_word, text.split())))


def _normalize_word(word: str) -> Optional[str]:
    """
    Normalize `word` to something ready for the word cloud.

    Steps:
    1. Check that `word` is not an email, URL, or mention
    2. Remove non-letter or underscore (`_`) characters from `word`
    3. Check that the stripped-down `word` is not a stop word or too short
    """
    if any(pat.match(word) for pat in stop_patterns):
        return None

    word = BAD_CHAR_PATTERN.sub("", word)

    if word in stop_words or len(word) < 2:
        return None

    return word
