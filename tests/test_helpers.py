import pytest

from tweetcloud import helpers


@pytest.mark.parametrize(
    "tweet, expected_words",
    # Test counting words correctly
    [
        ("test words nuke nuke words", {"words": 3, "test": 1, "gum": 5, "nuke": 2}),
        # Test ignoring stop_words
        ("in a other some go test", {"words": 1, "test": 1, "gum": 5}),
        # Test removing removing account handles
        #  (letters, numbers, and '_' allowed in handles)
        (
            "@testAccount great @TestAccountNum1 @testAccountHypen_1 nuke",
            {"words": 1, "great": 1, "nuke": 1, "gum": 5},
        ),
        # Test removing urls
        ("http://te.gov words https://test.co", {"words": 2, "gum": 5}),
        # Test removing emails
        (
            """test ttest++sdfsdflkj34+sdfa_sdf@gmail.co test+2@gmail.co
             test_12@ema-il.org test@email.com test-2@email.com""",
            {"words": 1, "gum": 5, "test": 1},
        ),
        # Test ignoring retweets
        ("RT @testAccount Some other tweet here", {"words": 1, "gum": 5}),
    ],
)
def test_normalize_and_split_tweet(tweet, expected_words):
    words = {"words": 1, "gum": 5}

    helpers.normalize_and_split_tweet(tweet, words)
    assert words == expected_words
