import datetime
import pytest
import os
import numpy as np
from PIL import Image


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

@pytest.mark.parametrize(
    "words, date, tmp_image_folder, screen_name",
    [
        (
            {"words": 15, "test":10, "name": 5},
            datetime.datetime(2020, 8, 1),
            "tests/test_images",
            "test_account",
         )
    ])
def test_create_worldcloud(words, date, tmp_image_folder, screen_name):
    test_image_path = helpers.create_wordcloud(words, date, tmp_image_folder, screen_name)

    known_image = Image.open("tests/known_images/test_wordcloud-" + date.strftime("%Y-%m-%d") + ".png")
    test_image = Image.open(test_image_path)

    # Check the difference in the images from https://redshiftzero.github.io/pytest-image/
    sum_sq_diff = np.sum((np.asarray(known_image).astype('float') - np.asarray(test_image).astype('float'))**2)

    if sum_sq_diff == 0:
        # Images are exactly the same
        pass
    else:
        normalized_sum_sq_diff = sum_sq_diff / np.sqrt(sum_sq_diff)
        assert normalized_sum_sq_diff < 0.001

    os.remove(test_image_path)
