import datetime
import pytest
import ast
import os
import shutil
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
    "word_set_file_name, date, screen_name",
    [
        (
            "small_word_set.txt",
            datetime.date(2020, 8, 1),
            "test_account_small",
         ),
        (
            "medium_word_set.txt",
            datetime.date(2018, 10, 12),
            "test_account_medium",
        ),
        (
            "large_word_set.txt",
            datetime.date(1999, 1, 1),
            "test_account_large",
        ),
        (
            "huge_word_set.txt",
            datetime.date(2000, 5, 31),
            "test_account_huge",
        ),
    ])
def test_create_wordcloud(word_set_file_name, date, screen_name):
    test_images_folder = "tests/test_images"

    # Create folder for test images
    if not os.path.isdir(test_images_folder):
        os.mkdir(test_images_folder)

    f = open("tests/word_sets/" + word_set_file_name, "r")
    words = ast.literal_eval(f.read())
    test_image_path = helpers.create_wordcloud(words, date, test_images_folder, screen_name)

    known_image = Image.open("tests/known_images/test_wordcloud-" + date.strftime("%Y-%m-%d") + ".png")
    test_image = Image.open(test_image_path)

    # Check the difference in the images
    # Pulled from https://redshiftzero.github.io/pytest-image/
    sum_sq_diff = np.sum((np.asarray(known_image).astype('float') - np.asarray(test_image).astype('float'))**2)

    if sum_sq_diff == 0:
        # Images are exactly the same
        pass
    else:
        normalized_sum_sq_diff = sum_sq_diff / np.sqrt(sum_sq_diff)
        assert normalized_sum_sq_diff < 0.001

    # Delete the test images
    shutil.rmtree(test_images_folder)
