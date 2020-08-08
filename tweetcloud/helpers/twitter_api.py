from math import ceil


def get_all_tweets(t, screen_name, number_of_tweets):
    """
    Get the specified number of tweets for `screen_name`.
    """
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
