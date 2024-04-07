"""Spotifire.

This module runs a stand-alone streamlit data app that displays interactive analysis of
my spotify data.

Example:
    To run the app simply run the following in an
    environment that has streamlit::

        $ streamlit run streamlit_app.py

TODOs:
    * Module todos
"""

import os
from glob import glob
from pathlib import Path

import pandas as pd
import streamlit as st

# Example data for debugging and development
# from vega_datasets import data as data_vega
# Get plotting utility
from data import generate_wordcloud, get_genre_count, get_wordcloud_image
from plotting import (
    get_altair_histogram,
    get_audiofeature_chart,
    get_audiofeature_distribution,
)
from util.util import download_file, get_playlist_df, get_top_tracks_df

# For getting png image from remote


# Path to the repo image folder
REPO_URL_ROOT = (
    "https://raw.githubusercontent.com/Strandgaard96/spotify-dashboard/master/"
)

# External files to download.
EXTERNAL_DEPENDENCIES = {}

st.set_page_config(page_title="Spotifire", layout="wide", page_icon=":fire:")

# Download external dependencies.
for filename in EXTERNAL_DEPENDENCIES.keys():
    download_file(filename, EXTERNAL_DEPENDENCIES)

# Hack to try and center image.
_, col2, _ = st.sidebar.columns([1, 1, 1])
# Sombra logo in sidebar
col2.image("images/sombra.png", width=110)
# What to put under the sidebar
st.sidebar.markdown(
    '<h4>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png"\
     alt="Streamlit logo" \
     height="16">&nbsp by <a href="https://github.com/Strandgaard96">Strandgaard96</a></h4>',
    unsafe_allow_html=True,
)


# Get file names in folder:
datasets = glob("data/playlists/*.csv")
datasets = [Path(file).stem for file in datasets]

# Temporarily disabled
# Solution to the authentification problem could be spotipy.oauth2.SpotifyPKCE
# datasets.append("Custom")

playlist_name = st.sidebar.selectbox(
    "Choose the dataset to analyze",
    datasets,
)

music_df = get_playlist_df(f"data/playlists/{playlist_name}.csv")

# Set a headline for the current view
st.title("Welcome to the audio feature analysis page :musical_note:")
st.write(
    """
    Here you will find different analysis and visualizations
    for the playlist selected in the sidebar :sunglasses:
    """
)

st.markdown(
    f"##### Snippet of the data contained in the selected playlist ({playlist_name}):"
)
st.dataframe(
    music_df.head(5)[
        [
            "artist",
            "danceability",
            "energy",
            "instrumentalness",
            "liveness",
            "speechiness",
            "valence",
        ]
    ],
)

# Generate wordcloud if one does not exist for the current playlist
if not os.path.isfile(f"data/playlists/{playlist_name}.png"):
    generate_wordcloud(
        genres_df=music_df[["genre", "artist"]], playlist_name=playlist_name
    )
image = get_wordcloud_image(playlist_name=playlist_name)

# Get histogram chart opbject
_, df, genre_artists_count = get_genre_count(genres_df=music_df[["genre", "artist"]])

# Get 10 largest genres and sort by count.
df_largest = (
    df.nlargest(10, "count").sort_values(by="count", ascending=False).reset_index()
)

# Get histogram for the 10 largest dataframe.
chart_genre_hist = get_altair_histogram(
    df_largest,
    genre_artists_count,
    domain=[0, max(df_largest["count"])],
    title="Top 10 Genres",
)

# Audio feature analysis
audio_features = [
    "danceability",
    "energy",
    "speechiness",
    "instrumentalness",
    "liveness",
    "valence",
]
st.markdown(
    """
---
#### **Features explained:**
There are a number of features and they can be defined like so:
- **Danceability:** Measure of how suitable a track is for dancing.
- **Acousticness:** Acousticness of track.
- **Energy:** Measure of intensity and activity in track.
- **Instrumentalness:** If the track contains no vocals.
- **Liveness:** Detects presence of audience, eg. measures if the track was performed live.
- **Loudness:** Loudness of track.
- **Speechiness:** Measure the presence of spoken words in contrast to rapped/sung words.
- **Valence:** Indicates how positive or happy a song is.

Here you can select songs from the playlist below to see the distribution of features in the songs

"""
)
tracks = st.multiselect(
    "Choose tracks to visualize:",
    list(music_df.index),
    [music_df.index[0], music_df.index[1]],
)
if not tracks:
    st.error("Please select at least one track!")
else:
    data = music_df[audio_features]
    data = data.loc[tracks]

    st.write("#### Chosen songs:", music_df["artist"].loc[tracks].sort_index())

    data = data.T.reset_index()
    data = pd.melt(data, id_vars=["index"]).rename(
        columns={"index": "Feature", "value": "Value", "track_name": "Song"}
    )
    chart_features = get_audiofeature_chart(data)

    # For debugging chart:
    # chart_features.show()

# Print both obtained charts
main_col1, main_col2 = st.columns([1, 1])
main_col1.altair_chart(chart_features, use_container_width=True, theme=None)
main_col2.altair_chart(chart_genre_hist, use_container_width=True)

# Print wordcloud analysis
st.markdown(
    """
---
### What genres do the playlist consist of?
Another way of visualizing genres in the playlist is to use a wordcloud:
"""
)
st.image(image)

# Look at obscure genres
# Get 10 largest genres and sort by count.
df_smallest = (
    df.nsmallest(30, "count").sort_values(by="count", ascending=False).reset_index()
)

# Get altair object
chart_genre_hist = get_altair_histogram(
    df_smallest, genre_artists_count, domain=[0, 1], title="Low count genres"
)

st.markdown(
    """
---
### What are some more obscure genres in the playlist?
Some genres only appear once, usually some very niche ones.
"""
)

# Write chart to page
st.altair_chart(chart_genre_hist, use_container_width=True)

# Distribution of audio features for playlist
st.markdown(
    """
---
### What is the audio feature distribution of the playlist?
Here we see a Kernel Density Estimate (KDE) plot together with histograms for all of the audio
features. Click the audio features on the right to remove/add them to the figure
"""
)
audio_feature_distribution_chart = get_audiofeature_distribution(
    music_df[audio_features]
)
st.plotly_chart(audio_feature_distribution_chart, use_container_width=True, theme=None)

# Time based analysis
top_tracks_df = get_top_tracks_df
# TODO analysis
