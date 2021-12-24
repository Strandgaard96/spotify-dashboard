"""Spotifire

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
import urllib
from collections import Counter, defaultdict

import pandas as pd
import streamlit as st
from matplotlib import cm
from wordcloud import WordCloud

# Example data for debugging and development
# from vega_datasets import data as data_vega

# Get plotting utility
from plotting import get_wordcloud_image, get_altair_histogram, get_audiofeature_chart


def main():
    """
    Backbone of app. Contains the pointer to the different
    pages.
    """
    # Set content width
    st.set_page_config(page_title="Spotifire", layout="wide", page_icon=":fire:")

    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("intro.md"))

    # Download external dependencies.
    for filename in EXTERNAL_DEPENDENCIES.keys():
        download_file(filename)

    # Hack to try and center image.
    _, col2, _ = st.sidebar.columns([1, 1, 1])
    # Sombra logo in sidebar
    col2.image("images/sombra.png", width=110)

    # Create sidebar for selecting app pages
    st.sidebar.title("Select an app mode below: ")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        ["Show instructions", "Run the app", "Show the source code"],
    )

    if app_mode == "Show instructions":
        st.sidebar.success('To continue select "Run the app".')
    elif app_mode == "Show the source code":
        # Empty empties the container to
        readme_text.empty()
        st.code(get_file_content_as_string("streamlit_app.py"))
    elif app_mode == "Run the app":
        readme_text.empty()
        run_the_app()

    # What to put under the sidebar
    st.sidebar.markdown(
        '<h4>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png"\
         alt="Streamlit logo" \
         height="16">&nbsp by <a href="https://github.com/Strandgaard96">Strandgaard96</a></h4>',
        unsafe_allow_html=True,
    )


# This file downloader demonstrates Streamlit animation.
def download_file(file_path):
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
                MEGABYTES = 2.0 ** 20.0
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
    genre_wordcloud.to_file(f"data/{playlist_name}.png")


def run_the_app():
    """Run analysis

    Args:
        None

    Returns:
        None
    """

    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # In this common pattern, we download data from an endpoint only once.
    @st.cache
    def load_metadata(url):
        return pd.read_csv(url)

    # Get the playlist data
    @st.cache
    def get_dataframe(data):

        # Define the dtypes for columns to ensure correct format for later analysis
        dtypes = {
            "artist": "str",
            "genre": "str",
            "album": "str",
            "track_name": "str",
            "track_id": "str",
            "danceability": "float",
            "energy": "float",
            "key": "str",
            "loudness": "float",
            "speechiness": "float",
            "instrumentalness": "float",
            "liveness": "float",
            "valence": "float",
            "tempo": "float",
            "duration_ms": "int",
            "time_signature": "int",
            "track_popularity": "float",
            "added_at": "str",
        }
        parse_dates = ["time_signature"]
        df = pd.read_csv(data, dtype=dtypes, parse_dates=parse_dates)

        return df.set_index("track_name")

    # Variable for the name of the playlist.
    # The same name used for the data file and wordcloud image
    # Should be extended to be a dynamic variable through user input.
    playlist_name = "$"

    music_df = get_dataframe(f"data/{playlist_name}.csv")

    # Set a headline for the current view
    st.title("Welcome to the audio feature analysis page :musical_note:")
    st.write(
        """
        Here you will find different analysis and visualizations of the playlist data.
        
        The user is free to interact with some of these visualizations and 
        chose specific tracks to show analysis for.
        """
    )
    # Uncomment these lines to peek at these DataFrames.
    st.write(
        "#### Here we print the five first songs in the data ",
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
    if not os.path.isfile(f"data/{playlist_name}.png"):
        generate_wordcloud(
            genres_df=music_df[["genre", "artist"]], playlist_name=playlist_name
        )
    image = get_wordcloud_image(playlist_name=playlist_name)

    # Get histogram chart opbject
    _, df, genre_artists_count = get_genre_count(
        genres_df=music_df[["genre", "artist"]]
    )

    # Get 10 largest genres and sort by count.
    df_largest = (
        df.nlargest(10, "count").sort_values(by="count", ascending=False).reset_index()
    )

    # Get histogram for the 10 largest dataframe.
    chart_genre_hist = get_altair_histogram(df_largest, genre_artists_count, domain=[0,max(df_largest['count'])], title='Top 10 Genres')

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
    - **Danceability:** Measure of how suitable a track is for dancing.
    - **Acousticness:** Acousticness of track.
    - **Energy:** Measure of intensity and activity in track.
    - **Instrumentalness:** If the track contains no vocals.
    - **Liveness:** Detects presence of audience. If the track was performed live.
    - **Loudness:** Loudness of track.
    - **Speechiness:** Measure the presence of spoken words in contrast to rapped/sung words.  
    - **Valence:** Indicates how positive or happy a song is.
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

        st.write("#### Chosen songs:", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "Feature", "value": "Value", "track_name": "Song"}
        )
        chart_features = get_audiofeature_chart(data)

        # For debugging chart:
        # chart_features.show()

    # Print both obtained charts
    main_col1, main_col2 = st.columns([1, 1])
    main_col1.altair_chart(chart_features, use_container_width=True)
    main_col2.altair_chart(chart_genre_hist, use_container_width=True)

    # Print wordcloud analysis
    st.markdown(
        """
    ---
    ### What genres do the playlist consist of?
    
    All the genres are visualized here in a wordcloud format:
    """
    )
    st.image(image)

    # Look at obscure genres
    # Get 10 largest genres and sort by count.
    df_smallest = (
        df.nsmallest(40, "count").sort_values(by="count", ascending=False).reset_index()
    )

    # Get altair object
    chart_genre_hist = get_altair_histogram(df_smallest, genre_artists_count, domain=[0,2],\
                                            title='40 lowest count genres')

    # Write chart to page
    st.altair_chart(chart_genre_hist, use_container_width=True)


# Download a single file and make its content available as a string.
@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    """Get markdown file from repo and return as string"""
    url = (
        "https://raw.githubusercontent.com/Strandgaard96/spotify-dashboard/master/"
        + path
    )
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

# Path to the repo image folder
REPO_URL_ROOT = (
    "https://raw.githubusercontent.com/Strandgaard96/spotify-dashboard/master/"
)

# External files to download.
EXTERNAL_DEPENDENCIES = {}

if __name__ == "__main__":
    main()
