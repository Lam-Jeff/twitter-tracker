import os
import tweepy
from dotenv import load_dotenv
from textblob import TextBlob
import re
from typing import Tuple

TWEET_CRAP_RE = re.compile(r"\bRT\b", re.IGNORECASE)
URL_RE = re.compile(r"(^|\W)https?://[\w./&%]+\b", re.IGNORECASE)
PURE_NUMBERS_RE = re.compile(r"(^|\W)\$?[0-9]+\%?", re.IGNORECASE)
EMOJI_RE = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        re.UNICODE,
    )
OTHER_REMOVALS_RE = re.compile("[" "\u2026" "]+", re.UNICODE)  # Ellipsis
SHORTHAND_STOPWORDS_RE = re.compile(
        r"(?:^|\b)("
        "w|w/|"  # Short for "with"
        "bc|b/c|"  # Short for "because"
        "wo|w/o"  # Short for "without"
        r")(?:\b|$)",
        re.IGNORECASE,
    )
AT_MENTION_RE = re.compile(r"(^|\W)@\w+\b", re.IGNORECASE)
HASH_TAG_RE = re.compile(r"(^|\W)#\w+\b", re.IGNORECASE)
PREFIX_CHAR_RE = re.compile(r"(^|\W)[#@]", re.IGNORECASE)

# loading env variables
load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")

def cleanText (text: str) -> str:
    """
    Clean the text using Regex expressions

    text -- the tweet
    return -- the tweet with the emojis in ascii
    """
    regexes = [
            EMOJI_RE,
            PREFIX_CHAR_RE,
            PURE_NUMBERS_RE,
            TWEET_CRAP_RE,
            OTHER_REMOVALS_RE,
            SHORTHAND_STOPWORDS_RE,
            URL_RE,
        ]

    for regex in regexes:
        text = regex.sub("", text)
    return text


def analyzeSentiment (tweets: dict) -> dict:
    """
    Compute the sentiment of a tweet.

    tweets -- a dictionary of tweets
    return -- a dictionary with the number of positive, neutral and negative tweets
    """
    Positive = 0
    Negative = 0
    Neutral = 0
    total_polarity = 0
    total_subjectivity = 0
    count = 0

    for tweet in tweets:
        count += 1
        cleaned_text = cleanText (tweet.text)
        sentiment = TextBlob(cleaned_text).sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity
        total_subjectivity += subjectivity
        total_polarity += polarity
        if polarity > 0 :
            Positive += 1
        elif polarity < 0 :
            Negative += 1
        else :
            Neutral += 1
        
    return ({"positive": Positive, "neutral": Neutral, "negative": Negative, "polarity": float(total_polarity / count), "subjectivity": float(total_subjectivity / count)});

def likesCount (data: list) -> int: 
    """
    Count the number of likes.

    data -- the structure containing all the users who like the tweet
    return -- the numbers of likes
    """
    count = 0
    if data:
        for user in data:
            count += 1
    return count

def wordsCount (tweets: dict) -> dict:
    """
    Count the number of occurrences for each word.

    tweet_text -- the tweets
    return -- a dictionary with the number of word occurrences
    """
    words_count = {}
    for tweet in tweets:
        words = cleanText (tweet.text).split()
        for word in words:
            if word in words_count:
                words_count[word] += 1
            else:
                words_count[word] = 1
    sorted_dict = {k: v for k, v in sorted(words_count.items(), key=lambda item: item[1], reverse=True)}
    return sorted_dict

def getTweets (search_word: str, number_tweets: int, retweet: bool, replies: bool) -> Tuple[dict, dict, dict, dict]:
    """
    Get the tweets corresponding to the search word and return all the tweets found with its sentiments and words count.

    search_word -- the word used to find the tweets
    number_tweets -- the number of tweets to return
    retweet -- a boolean to exclude retweet if true
    replies -- a boolean to exclude replies if true
    return -- a tuple of dictionaries
    """
    query = search_word
    if retweet:
        query += ' -is:retweet'
    if replies:
        query += ' -is:reply'
    client = tweepy.Client(bearer_token=bearer_token)

    response = client.search_recent_tweets(query=query, max_results=number_tweets, tweet_fields=['created_at', 'lang', 'author_id'], user_fields=['username'],expansions='entities.mentions.username')
    tweets = response.data
    sentiments = analyzeSentiment (tweets)
    words_count =  wordsCount (tweets)
    tweets_details = []
    for tweet in tweets:
        favorite_count = client.get_liking_users (id=tweet.id)
        
        tweets_details.append ({
            'likes': likesCount (favorite_count.data),
            'username': client.get_user(id=tweet.author_id).data['username'],
            'id': tweet.id
        })
    return tweets, tweets_details, sentiments, words_count
