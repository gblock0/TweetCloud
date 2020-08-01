# Welcome to TweetCloud!

![Build](https://github.com/gblock0/TweetCloud/workflows/BuildAndRunTests/badge.svg)


The goal of this project is generate a gif of word clouds from a specific Twitter user's tweets. Currently, 3000 is the max number of tweets that will be fetched from Twitter.

**NOTE**: This project is in development, so not all features will work or are finished! Feel free to open a PR if you'd like to contribute!

## Setup

1. [Create a Twitter app](https://developer.twitter.com/en/apps)
1. Install the package using `pip install git+https://github.com/gblock0/TweetCloud`
1. Add the following keys from your new Twitter app to your environment variables
   - `export TWTR_CONS_KEY=<TWITTER_CONSUMER_API_KEY>`
   - `export TWTR_CONS_SEC=<TWITTER_CONSUMER_API_SECRET_KEY>`
   - `export TWTR_ACC_KEY=<TWITTER_ACCESS_TOKEN>`
   - `export TWTR_ACC_SEC=<TWITTER_TOKEN_SECRET>`

## How to use

`tweetcloud <screen_name> <number_of_tweets>`

### Example

Running `tweetcloud nasa 1000` generates:

![TweetCloud Demo](nasa-2020-05-24-to-2020-07-26.gif)

## Developing

1. Clone repo
1. Create new environment from environment.yml: `conda env create -f environment.yml`
1. Activate environment and install using `--editable`: `pip install -e ".[dev]"`
1. Run tests with `pytest tests/`
1. Run `pre-commit run --all-files` before opening a PR please

## Contributors

- [jgoldfinger](https://github.com/jgoldfinger)
- [onepan](https://github.com/onepan)
