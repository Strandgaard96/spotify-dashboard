"""Module for doing playlist manipulations."""
import json
from collections import Counter, defaultdict
from io import BytesIO
from random import randint

import pandas as pd
import requests
import streamlit as st
from matplotlib import cm
from PIL import Image
from wordcloud import WordCloud


def get_genre_count(genres_df=None):
    """Utility method to extract genres from the dataframe into list.

    Args:
        genres_df (DataFrame):

    Returns:
        genres_count (iterable of int): How many songs of each genre
        df (DataFrame): Dataframe containing number of each genre and a set of corresponding artists.
        genre_artists_count (nested dict with iterable of strings): Counter objects for each genre
    """

    # Initialize list to hold all genre entries
    genres_long = []

    # Dictionary to hold all the artists for a genre. The artist is added to the genre list of artists
    # each time a new song within the genre by the artists appears.
    genre_artists = defaultdict(list)

    # Dict to hold counter iterables for each genre
    genre_artists_count = defaultdict()

    # Loop the songs and get all genres for song. Add to genres list
    for _, row in genres_df.iterrows():
        genres_long.extend(list(row["genre"].split("/")))
        # Add the artist for the current song to each of the genre entries.
        for elem in list(row["genre"].split("/")):
            genre_artists[elem].append(row["artist"])

    # Count how many times an artist contributes to genre and order according to highest.
    for elem in genre_artists:

        # For a genre, count the unique artists and their num entries
        genre_artists_count[elem] = Counter(genre_artists[elem])

        # Sort the artists for each genre according to the ones appearing most from high to low.
        genre_artists[elem] = list(
            dict.fromkeys(
                sorted(
                    genre_artists[elem],
                    key=Counter(genre_artists[elem]).get,
                    reverse=True,
                )
            )
        )
        # Explanation of above snippet. sorted takes a list that is the artists for a certain genre
        # Then sorts based on the function given by key.
        # This is turned into dict of artist names and then into list.

    # Count the occurrence of each genre which is used as base for dataframe
    genres_count = Counter(genres_long)

    # DataFrame with genre and count columns.
    df = (
        pd.DataFrame.from_dict(genres_count, orient="index")
        .reset_index()
        .rename(columns={"index": "genre", 0: "count", 1: "artists"})
    )
    # Add the list of artists for each genre.
    df["artists"] = df["genre"].map(genre_artists)

    return genres_count, df, genre_artists_count


def generate_wordcloud(genres_df=None, playlist_name=None):
    """

    Args:
        genres_df (DataFrame): Songs as index and columns of artist and genre list
        playlist_name (str): Name of playlist to generate wordcloud from

    Returns:
        None
    """
    # Inspo from :
    # https://oleheggli.medium.com/easily-analyse-audio-features-from-spotify-playlists-part-3-ec00a55e87e4

    genre_wordcloud = WordCloud(
        stopwords="unknown",
        height=500,
        width=1000,
        min_font_size=4,
        colormap=cm.get_cmap("tab10"),
        include_numbers=True,
    )
    genres_count, _, _ = get_genre_count(genres_df=genres_df)
    genre_wordcloud.generate_from_frequencies(genres_count)
    genre_wordcloud.to_file(f"data/playlists/{playlist_name}.png")


@st.cache
def get_wordcloud_image(playlist_name=None):
    """Get wordcloud image from repo (which is cached by streamlit
    decorator)"""
    image = Image.open(f"data/playlists/{playlist_name}.png")
    return image


def get_comic():
    try:
        with requests.Session() as s:
            content = s.get("https://xkcd.com/info.0.json").content.decode()
            data = json.loads(content)
            HighestNumber = data["num"]

            random = True
            if random:
                rand_digits = randint(1, HighestNumber)
                endpoint = "https://xkcd.com/{}/info.0.json".format(rand_digits)
                content = s.get(endpoint).content.decode()
                data = json.loads(content)
                res = s.get(data["img"])
                img = Image.open(BytesIO(res.content))
            else:
                res = s.get(data["img"])
                img = Image.open(BytesIO(res.content))
    except requests.ConnectionError:
        img = Image.open("data/comic.png")
        # error_image = Image.open("assets/xkcd_404.jpg")
        # error_image.show()
    return img
