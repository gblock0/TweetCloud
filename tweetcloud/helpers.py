import html
import re
from math import ceil

import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import STOPWORDS, WordCloud

# Stop Words
stop_words = {"go", "will"}.union(set(STOPWORDS))


# Normalize the tweet:
#   - Remove mentions, emails, and websites
#   - Disregard retweeted tweets
def normalize_and_split_tweet(tweet, words):
    full_text = html.unescape(tweet)
    match_rt = full_text.startswith("RT @")

    # Remove mentions
    normalized_full_text = re.sub(r"(\A){0,1}@[\d\w]*(\s|\Z){1}", "", full_text)

    # Remove emails
    normalized_full_text = re.sub(
        r"(\A){0,1}[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}(\s|\Z){1}",
        "",
        normalized_full_text,
    )

    # Only look at words that weren't in retweeted tweets and are more than 1 character
    if not match_rt and len(normalized_full_text) > 0:
        words_in_tweet = normalized_full_text.split()
        for word in words_in_tweet:
            match_website = re.search("^http[s]?://", word)
            normalized_word = re.sub(r"[\W\d]+", "", word.lower())
            if (
                normalized_word not in stop_words
                and len(normalized_word) > 1
                and not match_website
            ):
                if normalized_word in words:
                    words[normalized_word] += 1
                else:
                    words[normalized_word] = 1


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

    return Image.open(file_path)
