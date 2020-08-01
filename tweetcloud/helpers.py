import collections
import datetime
import html
import operator
import re
from functools import reduce
from itertools import groupby
from math import ceil
from typing import Counter, Dict, Final, Iterable, Optional

import matplotlib.pyplot as plt
import twitter
from PIL import Image
from wordcloud import STOPWORDS, WordCloud

# Stop Words
stop_words: Final = {"go", "will"}.union(set(STOPWORDS))

URL_PATTERN: Final = re.compile(r"https?://")
EMAIL_PATTERN: Final = re.compile(r"[\w.\-+%]+@[\w.\-]+\.[a-zA-Z]{2,}")
MENTIONS_PATTERN: Final = re.compile(r"@\w+")
stop_patterns: Final = (URL_PATTERN, MENTIONS_PATTERN, EMAIL_PATTERN)

BAD_CHAR_PATTERN: Final = re.compile(r"[\W\d]+")


def transform_tweets_to_word_counts(
    tweets: Iterable[twitter.models.Status],
) -> Dict[datetime.date, Counter[str]]:
    """
    Group tweets and return normalized word counts per group.
    """
    groups = groupby(sorted(tweets, key=_tweet_group_key), key=_tweet_group_key)
    # Lots of iteration here. If we start processing tons of tweets
    # it might be noticeable, but if it comes to that we should use
    # a proper text processing library.
    return {
        key: reduce(operator.add, map(normalize_and_split_tweet, group))
        for key, group in groups
    }


def _tweet_group_key(tweet: twitter.models.Status) -> datetime.date:
    """
    Get the grouping key for each tweet, i.e., the Sunday prior to the
    tweet's date.
    """
    tweet_date = datetime.datetime.utcfromtimestamp(tweet.created_at_in_seconds)
    return tweet_date.date() - datetime.timedelta(days=tweet_date.weekday() + 1)


# todo: mock a Status object in tests
def normalize_and_split_tweet(tweet: twitter.models.Status) -> Counter[str]:
    """
    Convert a tweet's text into normalized term counts.

    Temporary wrapper to avoid mocking in tests
    """
    return _normalize_and_split_text(tweet.full_text)


def _normalize_and_split_text(raw_text: str) -> Counter[str]:
    """
    Convert a tweet's text into normalized term counts.
    """
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
    Remove non-letter or underscore (`_`) characters from `word`.
    """
    if any(pat.match(word) for pat in stop_patterns):
        return None

    word = BAD_CHAR_PATTERN.sub("", word)

    if word in stop_words or len(word) < 2:
        return None

    return word


# Gets the number tweets for a screen_name specified in the command line args
def get_all_tweets(t, screen_name, number_of_tweets):
    count = max_count_from_twitter = 200
    number_of_extra_api_calls = 0
    if number_of_tweets < max_count_from_twitter:
        count = number_of_tweets
    elif number_of_tweets > max_count_from_twitter:
        number_of_extra_api_calls = ceil(
            (number_of_tweets - max_count_from_twitter) / max_count_from_twitter
        )
    all_tweets = t.GetUserTimeline(
        screen_name=screen_name, count=count, include_rts=False
    )
    last_id = all_tweets[-1].id
    number_of_tweets_to_find = number_of_tweets - count

    for _ in range(number_of_extra_api_calls):
        if number_of_tweets_to_find < max_count_from_twitter:
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
def create_wordcloud(words, date, tmp_image_folder, screen_name):
    wordcloud = WordCloud(
        width=950, height=950, background_color="white", min_font_size=10
    ).generate_from_frequencies(words)
    plt.figure(figsize=(9.5, 10), facecolor=None)
    plt.title(
        "Words seen the week of " + str(date) + " in " + screen_name + "'s tweets",
        {"fontsize": 18, "fontweight": 600},
        pad=20,
    )
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.imshow(wordcloud)
    file_path = tmp_image_folder + "/image-" + str(date) + ".png"
    plt.savefig(file_path)
    plt.close()

    return Image.open(file_path)
