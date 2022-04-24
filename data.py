"""
Module for doing playlist manipulations
"""
import os
import sqlite3
import urllib
from collections import defaultdict, Counter

import pandas
import pandas as pd
import streamlit as st
from matplotlib import cm
from wordcloud import WordCloud


def download_file(file_path, EXTERNAL_DEPENDENCIES):
    """
    Downloads files specified by EXTERNAL_DEPENDENCIES to current directory.
    The keys are the filenames of the downloaded files.
    Args:
        file_path (str): Path to file to download
    Returns:
        None
    """

    # Don't download the file twice. (If possible, verify the download using
    # the file length.)
    if os.path.exists(file_path):
        if "size" not in EXTERNAL_DEPENDENCIES[file_path]:
            return
        elif os.path.getsize(file_path) == EXTERNAL_DEPENDENCIES[file_path]["size"]:
            return

    # These are handles to two visual elements to animate.
    weights_warning, progress_bar = None, None
    try:
        weights_warning = st.warning("Downloading %s..." % file_path)
        progress_bar = st.progress(0)
        with open(file_path, "wb") as output_file:
            with urllib.request.urlopen(
                EXTERNAL_DEPENDENCIES[file_path]["url"]
            ) as response:
                length = int(response.info()["Content-Length"])
                counter = 0.0
                MEGABYTES = 2.0**20.0
                while True:
                    data = response.read(8192)
                    if not data:
                        break
                    counter += len(data)
                    output_file.write(data)

                    # We perform animation by overwriting the elements.
                    weights_warning.warning(
                        "Downloading %s... (%6.2f/%6.2f MB)"
                        % (file_path, counter / MEGABYTES, length / MEGABYTES)
                    )
                    progress_bar.progress(min(counter / length, 1.0))

    # Finally, we remove these visual elements by calling .empty().
    finally:
        if weights_warning is not None:
            weights_warning.empty()
        if progress_bar is not None:
            progress_bar.empty()


def get_genre_count(genres_df=None):
    """
    Utility method to extract genres from the dataframe into list

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
        colormap=cm.inferno,
        include_numbers=True,
    )
    genres_count, _, _ = get_genre_count(genres_df=genres_df)
    genre_wordcloud.generate_from_frequencies(genres_count)
    genre_wordcloud.to_file(f"data/playlists/{playlist_name}.png")


@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    """Get markdown file from repo and return as string"""
    url = (
        "https://raw.githubusercontent.com/Strandgaard96/spotify-dashboard/master/"
        + path
    )
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")
