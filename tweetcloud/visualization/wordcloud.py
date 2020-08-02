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
