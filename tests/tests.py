from tweetcloud import helpers


def test_normalize_and_split_tweet():
    words = {"words": 1, "gum": 5}

    # Test counting words correctly
    tweet = "test words nuke nuke words"
    helpers.normalize_and_split_tweet(tweet, words)
    assert words == {"words": 3, "test": 1, "gum": 5, "nuke": 2}

    # Test ignoring stop_words
    stop_words_tweet = "in a other some go test"
    helpers.normalize_and_split_tweet(stop_words_tweet, words)
    assert words == {"words": 3, "test": 2, "gum": 5, "nuke": 2}

    # Test removing account handles (letters, numbers, and '_')
    account_handles_tweet = (
        "@testAccount great @TestAccountNum1 @testAccountHypen_1 nuke"
    )
    helpers.normalize_and_split_tweet(account_handles_tweet, words)
    assert words == {"words": 3, "test": 2, "gum": 5, "nuke": 3, "great": 1}

    # Test removing urls
    urls_tweet = "http://te.gov words https://test.co"
    helpers.normalize_and_split_tweet(urls_tweet, words)
    assert words == {"words": 4, "test": 2, "gum": 5, "nuke": 3, "great": 1}

    # Test removing emails
    emails_tweet = "test ttest++sdfsdflkj34+sdfa_sdf@gmail.co test+2@gmail.co "
    emails_tweet += "test_12@ema-il.org test@email.com test-2@email.com"
    helpers.normalize_and_split_tweet(emails_tweet, words)
    assert words == {"words": 4, "test": 3, "gum": 5, "nuke": 3, "great": 1}

    rt_tweet = "RT @testAccount Some other tweet here"
    helpers.normalize_and_split_tweet(rt_tweet, words)
    assert words == {"words": 4, "test": 3, "gum": 5, "nuke": 3, "great": 1}
