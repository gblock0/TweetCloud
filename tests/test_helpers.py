from collections import Counter

import pytest

from tweetcloud import helpers


@pytest.mark.parametrize(
    "text, expected_words",
    # Test counting words correctly
    [
        ("test words nuke nuke words", Counter({"words": 2, "test": 1, "nuke": 2})),
        # Test ignoring stop_words
        ("in a other some go test", Counter({"test": 1})),
        # Test removing removing account handles
        #  (letters, numbers, and '_' allowed in handles)
        (
            "@testAccount great @TestAccountNum1 @testAccountHypen_1 nuke",
            Counter({"great": 1, "nuke": 1}),
        ),
        # Test removing urls
        ("http://te.gov words https://test.co", Counter({"words": 1})),
        # Test removing emails
        (
            """test ttest++sdfsdflkj34+sdfa_sdf@gmail.co test+2@gmail.co
             test_12@ema-il.org test@email.com test-2@email.com""",
            Counter({"test": 1}),
        ),
        # Test ignoring retweets
        ("RT @testAccount Some other tweet here", Counter()),
        # Test removing non-letter or `_` characters from words
        (
            "So_me words1 w1th numb3r$ a.nd ",
            Counter({"words": 1, "so_me": 1, "wth": 1, "numbr": 1}),
        ),
    ],
)
def test_normalize_and_split_text(text, expected_words):
    actual_words = helpers._normalize_and_split_text(text)
    assert actual_words == expected_words
