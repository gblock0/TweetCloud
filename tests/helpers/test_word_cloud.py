import datetime
import json
import os
import shutil

import numpy as np
import pytest
from PIL import Image
from tweetcloud.visualization import wordcloud

@pytest.mark.parametrize(
    "word_set_file_name, date, screen_name",
    [
        ("small_word_set.txt", datetime.date(2020, 8, 1), "test_account_small",),
        ("medium_word_set.txt", datetime.date(2018, 10, 12), "test_account_medium",),
        ("large_word_set.txt", datetime.date(1999, 1, 1), "test_account_large",),
        ("huge_word_set.txt", datetime.date(2000, 5, 31), "test_account_huge",),
    ],
)
def test_create_wordcloud(word_set_file_name, date, screen_name):
    test_images_folder = "tests/test_images"

    # Create folder for test images
    if not os.path.isdir(test_images_folder):
        os.mkdir(test_images_folder)

    with open("tests/word_sets/" + word_set_file_name) as word_set:
        words = json.load(word_set)
        test_wordcloud = wordcloud.create_wordcloud(
            words, date, test_images_folder, screen_name
        )

        known_image = Image.open(
            "tests/known_images/test_wordcloud-" + date.strftime("%Y-%m-%d") + ".png"
        )

        test_image = test_wordcloud

        # Check the difference in the images
        norm = np.linalg.norm(
            np.array(known_image, dtype="float") - np.array(test_image, dtype="float")
        )
        assert norm < 0.001

        # Delete the test images
        shutil.rmtree(test_images_folder)
