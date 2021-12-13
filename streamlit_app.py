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
from collections import Counter

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image
from matplotlib import cm
from wordcloud import WordCloud


# Example data for debugging and development
# from vega_datasets import data as data_vega


def main():
    """
    Backbone of app. Containts the pointer to the different
    pages.
    """
    # Set contenct width
    st.set_page_config(page_title="Spotifire", layout="wide", page_icon=":fire:")

    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("intro.md"))

    # Download external dependencies.
    for filename in EXTERNAL_DEPENDENCIES.keys():
        download_file(filename)

    _, col2, _ = st.sidebar.columns([1, 1, 1])
    # Smbra logo in sidebar
    col2.image(REPO_URL_ROOT + "images/sombra.png", width=120)

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
    :param file_path:
    :return: None
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
    :return: list : genres DataFrame: df
    """

    # Get all genres as long list
    genres_long = []
    for this_track in genres_df:
        genres_long.extend(list(this_track.split("/")))

    # Count the occurrence of each genre
    genres_count = Counter(genres_long)
    df = (
        pd.DataFrame.from_dict(genres_count, orient="index")
        .reset_index()
        .rename(columns={"index": "genre", 0: "count"})
    )
    return genres_count, df


@st.cache
def generate_wordcloud(genres_df=None):
    "Wordcloud generator"
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
    genres_count, _ = get_genre_count(genres_df=genres_df)
    genre_wordcloud.generate_from_frequencies(genres_count)
    genre_wordcloud.to_file("data/cloud.png")


@st.cache
def get_wordcloud_image():
    """Get wordcloud image from repo"""
    image = Image.open("data/cloud.png")
    return image


def run_the_app():
    """
    Runs the data analysis
    :return: None
    """

    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # In this common pattern, we download data from an endpoint only once.
    @st.cache
    def load_metadata(url):
        return pd.read_csv(url)

    # Get the playlist data
    @st.cache
    def get_dataframe(data):
        df = pd.read_csv(data)
        return df.set_index("track_name")

    # An amazing property of st.cached functions is that you can pipe them into
    # one another to form a computation DAG (directed acyclic graph). Streamlit
    # recomputes only whatever subset is required to get the right answer!
    music_df = get_dataframe(
        "https://raw.githubusercontent.com/Strandgaard96/spotify-dashboard/master/data/$.csv"
    )

    # Set a headline for the current view
    st.title("Audio feature analysis")
    st.markdown("This page contains some simple visualizations of the playlist data")
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

    # Generate wordcloud and obtain
    generate_wordcloud(genres_df=music_df["genre"])
    image = get_wordcloud_image()

    # Get histogram chart opbject
    count, df = get_genre_count(genres_df=music_df["genre"])
    df = df.nlargest(10, "count").sort_values(by="count", ascending=False)
    chart_genre_hist = get_altair_histogram(df)

    # Get audio feature analysis
    chart_features = show_audio_features(music_df=music_df)

    # Print both obtained charts
    main_col1, main_col2 = st.columns([1, 1])
    main_col1.altair_chart(chart_features, use_container_width=True)
    main_col2.altair_chart(chart_genre_hist, use_container_width=True)

    # Print wordcloud analysis
    st.write("---")
    st.markdown("### What genres does the playlist consist of?")
    st.markdown("Wordcloud showing the genre distribution:")
    st.image(image)


def get_altair_histogram(data=None):
    """
    Create a histogram of the most common genres
    :param data:
    :return: alt.Chart : hist
    """

    hist = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X(
                "genre",
                axis=alt.Axis(title="Genre"),
                sort=alt.EncodingSortField(order="ascending"),
            ),
            y=alt.Y("count", axis=alt.Axis(title="Counts")),
        )
        .properties(width=200, height=600, title="Top 10 genres")
        .configure_axis(labelFontSize=16, titleFontSize=16, labelAngle=-45)
        .configure_title(
            fontSize=20,
        )
    )
    # Can be added to enable scroll and zoom in the chart
    # .interactive()

    return hist


def show_audio_features(music_df=None):
    """
    Take the music dataframe and create ui element that user can interact with
    to visualize different audio features
    :param music_df:
    :return: Drawn plot (None)
    """
    audio_features = [
        "danceability",
        "energy",
        "speechiness",
        "instrumentalness",
        "liveness",
        "valence",
    ]
    tracks = st.multiselect(
        "Choose track to visualize", list(music_df.index), ["Gold Digger", "Shake That"]
    )
    if not tracks:
        st.error("Please select at least one track!")
    else:
        data = music_df[audio_features]
        data = data.loc[tracks]

        st.write("#### Chosen songs:", data.sort_index())
        st.write("---")
        # TODO explain features
        st.markdown(
            """
        **Features explained:**
       
        """
        )

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "Feature", "value": "Value", "track_name": "Song"}
        )
        chart_features = get_audiofeature_chart(data)

        return chart_features


def get_audiofeature_chart(data):
    chart_features = (
        alt.Chart(data)
        .mark_area(opacity=0.3)
        .encode(
            x="Feature",
            y=alt.Y("Value", stack=None, scale=alt.Scale(domain=[0, 1])),
            color="Song",
        )
        .configure_axis(labelFontSize=16, titleFontSize=16, labelAngle=-45)
        .properties(title="Audio features", height=500)
        .configure_title(
            fontSize=20,
        )
        .configure_legend(symbolSize=250, titleFontSize=25, labelFontSize=25)
    )
    return chart_features


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
