import csv
import datetime
import json
from collections import Counter
from pathlib import Path

import pytest
from twitter import Status

from tweetcloud.helpers import text as texthelper

tweet_data = json.loads(Path("tests/helpers/data/tweets.json").read_text())
word_data = list(
    csv.reader(Path("tests/helpers/data/words.csv").read_text().splitlines())
)


@pytest.fixture
def single_tweet(request):
    single_spec = request.param
    tweet = Status(
        full_text=single_spec["full_text"], created_at=single_spec["created_at"],
    )
    expected = {
        "word_counts": Counter(single_spec["counts"]),
        "group": datetime.date.fromisoformat(single_spec["group"]),
    }
    return tweet, expected


@pytest.fixture
def grouped_tweets():
    tweets = [
        Status(
            full_text=single_spec["full_text"], created_at=single_spec["created_at"],
        )
        for single_spec in tweet_data["tweets"]
    ]

    expected_word_counts = {
        datetime.date.fromisoformat(key): value
        for key, value in tweet_data["counts"].items()
    }
    return tweets, expected_word_counts


@pytest.mark.parametrize(
    "single_tweet",
    tweet_data["tweets"],
    indirect=True,
    ids=[single_spec["id"]["normalize"] for single_spec in tweet_data["tweets"]],
)
def test_normalize_and_split_tweet(single_tweet):
    tweet, expected = single_tweet
    expected_word_counts = expected["word_counts"]
    actual_word_counts = texthelper.normalize_and_split_tweet(tweet)
    assert actual_word_counts == expected_word_counts


def test_transform_tweets_to_word_counts(grouped_tweets):
    tweets, expected_word_counts = grouped_tweets
    actual_word_counts = texthelper.transform_tweets_to_word_counts(tweets)
    assert actual_word_counts == expected_word_counts


@pytest.mark.parametrize(
    "single_tweet",
    tweet_data["tweets"],
    indirect=True,
    ids=[single_spec["id"]["group"] for single_spec in tweet_data["tweets"]],
)
def test__tweet_group_key(single_tweet):
    tweet, expected = single_tweet
    expected_group = expected["group"]
    actual_group = texthelper._tweet_group_key(tweet)
    assert actual_group == expected_group
    assert actual_group.weekday() == 0


@pytest.mark.parametrize("word, expected", word_data)
def test__normalize_word(word, expected):
    actual = texthelper._normalize_word(word)
    actual = "" if actual is None else actual
    assert actual == expected
