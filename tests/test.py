from tweetcloud import helpers

def test_normalize():
    tweet = "test words test@email.com https://test.co nuke some other nuke words"
    words = {"words": 1, "gum":5}
    helpers.normalize_and_split_tweet(tweet, words)
    assert words == {"words":3, "test": 1, "gum":5, "nuke": 2}
