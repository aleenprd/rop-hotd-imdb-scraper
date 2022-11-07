"""Methods related to feature engineering."""


import pandas as pd
from datetime import datetime

import nltk

nltk.download("stopwords")
nltk.download("word_tokenize")
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("omw-1.4")

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

from typing import List


def clean_text(
    x: str, stop_words: nltk.corpus.reader.wordlist.WordListCorpusReader
) -> List[str]:
    """Tokenize, remove stop words, lemmatize, drop 'empty' tokens, drop non-alphanumeric characters.

    Args:
        x (str): a string of tokens.
        stop_words (nltk.corpus.reader.wordlist.WordListCorpusReader): a corpus of stop words.

    Returns:
        x (List[str]): cleaned text.
    """
    x = word_tokenize(x)
    x = [w for w in x if not w in stop_words]
    x = [lemmatizer.lemmatize(w) for w in x]
    x = [w for w in x if w != ""]
    x = [w for w in x if w.isalpha()]

    return x


def rating_to_cat(x: int) -> str:
    """Turn a 0-10 review scale to categorical values.

    Args:
        x (int): a number between 1 and 10.

    Returns:
        a value in [abysmal, bad, average, good, amazing].
    """
    if x in [1, 2]:
        return "abysmal"
    elif x in [3, 4]:
        return "bad"
    elif x in [5, 6]:
        return "average"
    elif x in [7, 8]:
        return "good"
    else:
        return "amazing"


def rating_to_5_scale(x: int) -> int:
    """Turn a 0-10 review scale to a 1-5 scale (like starts).

    Args:
        x (int): a number between 1 and 10.

    Returns:
        a value between 1 and 5.
    """
    if x in [1, 2]:
        return 1
    elif x in [3, 4]:
        return 2
    elif x in [5, 6]:
        return 3
    elif x in [7, 8]:
        return 4
    else:
        return 5


def clean_scraped_data(df: pd.DataFrame) -> pd.DataFrame:
    """Takes a dataframe fresh out of the scraper and enriches/cleans it.

    Args:
        df (pd.DataFrame): a scraped dataframe.

    Returns:
        pd.DataFrame: an enriched dataframe.
    """
    # Remove reviews without a rating
    df = df.dropna(subset=["review_rating"])

    # Get date from string
    df["review_date"] = df["review_date"].apply(
        lambda x: datetime.strptime(x, "%d %B %Y")
    )

    # I want to restrict these float values to integers because they are real numbers
    df["num_helpful_reactions"] = df["num_helpful_reactions"].astype(int)
    df["num_total_reactions"] = df["num_total_reactions"].astype(int)
    df["review_rating"] = df["review_rating"].astype(int)

    # I want to derive a ratio to denote the appreciation of a review (goes from 0 to 100)
    df["review_score"] = round(
        df["num_helpful_reactions"] / df["num_total_reactions"] * 100, 2
    )

    # Keep original text in place
    # I want to lowercase all the text.
    df["review_title_original"] = df["review_title"]
    df["review_text_original"] = df["review_text"]

    # I want to lowercase all the text.
    df["review_title"] = df["review_title"].apply(lambda x: x.lower())
    df["review_text"] = df["review_text"].apply(lambda x: x.lower())

    # Get length of non-tokenized title and text
    df["review_title_len_no_token"] = df["review_title"].apply(lambda x: len(x))
    df["review_text_len_no_token"] = df["review_text"].apply(lambda x: len(x))

    # I want to get the full text including title and review itself for later analysis
    df["full_review_text"] = df["review_title"] + " " + df["review_text"]

    # Tokenize text columns
    df["review_title_clean"] = df["review_title"].apply(
        lambda x: clean_text(x, stop_words)
    )
    df["review_text_clean"] = df["review_text"].apply(
        lambda x: clean_text(x, stop_words)
    )
    df["full_review_text_clean"] = df["full_review_text"].apply(
        lambda x: clean_text(x, stop_words)
    )

    # Get length of tokenized title and text
    df["clean_review_title_num_tokens"] = df["review_title_clean"].apply(
        lambda x: len(x)
    )
    df["clean_review_text_num_tokens"] = df["review_text_clean"].apply(lambda x: len(x))

    # Get the clean text back to string format
    df["review_title_clean"] = df["review_title_clean"].apply(lambda x: " ".join(x))
    df["review_text_clean"] = df["review_text_clean"].apply(lambda x: " ".join(x))
    df["full_review_text_clean"] = df["full_review_text_clean"].apply(
        lambda x: " ".join(x)
    )

    # Get length of tokenized title and text
    df["clean_review_title_len"] = df["review_title_clean"].apply(lambda x: len(x))
    df["clean_review_text_len"] = df["review_text_clean"].apply(lambda x: len(x))

    # Derive a categorified review scale
    df["review_rating_categorical"] = df["review_rating"].apply(
        lambda x: rating_to_cat(x)
    )
    df["review_rating_5_scale"] = df["review_rating"].apply(
        lambda x: rating_to_5_scale(x)
    )
    df["review_sentiment"] = df["review_rating"].apply(lambda x: 0 if x <= 5 else 1)

    return df
