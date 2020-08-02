import datetime
import tempfile
from typing import Counter, Dict

import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud


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


def create_animation(
    word_counts: Dict[datetime.date, Counter[str]], screen_name: str
) -> str:
    word_clouds = []
    sorted_dates = sorted(word_counts)
    start_date = sorted_dates[0]
    end_date = sorted_dates[-1]
    filename = f"{screen_name}-{start_date:%Y-%m-%d}-to-{end_date:%Y-%m-%d}.gif"

    with tempfile.TemporaryDirectory(prefix="tweetcloud-") as tmpdir:
        for date in sorted_dates:
            word_clouds.append(
                create_wordcloud(word_counts[date], date, tmpdir, screen_name)
            )

        word_clouds[0].save(
            filename,
            save_all=True,
            append_images=word_clouds[1:],
            optimized=False,
            duration=3000,
            loop=0,
        )
    return filename
