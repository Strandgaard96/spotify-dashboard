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

import pandas as pd
import streamlit as st
from glob import glob
from pathlib import Path

# Example data for debugging and development
# from vega_datasets import data as data_vega

# Get plotting utility
from data import (
    download_file,
    get_genre_count,
    generate_wordcloud,
    get_file_content_as_string,
)
from plotting import (
    get_wordcloud_image,
    get_altair_histogram,
    get_audiofeature_chart,
    get_audiofeature_distribution,
)
from streaming_data import get_streaming_barplot
from util.util import get_playlist_df, aquire_data_app, get_top_tracks_df


def main():
    """
    Backbone of app. Contains the pointer to the different
    pages.
    """
    # Set content width
    st.set_page_config(page_title="Spotifire", layout="wide", page_icon=":fire:")

    # Download external dependencies.
    for filename in EXTERNAL_DEPENDENCIES.keys():
        download_file(filename, EXTERNAL_DEPENDENCIES)
    # Hack to try and center image.
    _, col2, _ = st.sidebar.columns([1, 1, 1])
    # Sombra logo in sidebar
    col2.image("images/sombra.png", width=110)

    # Create sidebar for selecting app pages
    # Add aquire data string here to reactivate the functionality
    st.sidebar.title("Select an app mode below: ")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        ["Show instructions", "Run the app", "Show the source code"],
        index=0,
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

    readme_text = st.markdown("")

    if playlist_name == "Custom":
        app_mode = "Aquire data"

    if app_mode == "Show instructions":
        # Render the readme as markdown using st.markdown.
        readme_text = st.markdown(get_file_content_as_string("intro.md"))
        st.sidebar.success('To continue select "Run the app".')
    elif app_mode == "Show the source code":
        # Empty empties the container to
        readme_text.empty()
        st.code(get_file_content_as_string("streamlit_app.py"))
    elif app_mode == "Run the app":
        readme_text.empty()
        run_the_app(playlist_name=playlist_name)
    elif app_mode == "Aquire data":
        readme_text.empty()
        aquire_data_app()

    # What to put under the sidebar
    st.sidebar.markdown(
        '<h4>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png"\
         alt="Streamlit logo" \
         height="16">&nbsp by <a href="https://github.com/Strandgaard96">Strandgaard96</a></h4>',
        unsafe_allow_html=True,
    )


def run_the_app(playlist_name="$"):
    """Run analysis page

    Args:
        None

    Returns:
        None
    """

    # Variable for the name of the playlist.
    # The same name used for the data file and wordcloud image
    # Should be extended to be a dynamic variable through user input.

    music_df = get_playlist_df(f"data/playlists/{playlist_name}.csv")

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
    if not os.path.isfile(f"data/playlists/{playlist_name}.png"):
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
    chart_genre_hist = get_altair_histogram(
        df_smallest, genre_artists_count, domain=[0, 2], title="40 lowest count genres"
    )

    st.markdown(
        """
    ---
    ### What are some more obscure genres in the playlist?
    """
    )

    # Write chart to page
    st.altair_chart(chart_genre_hist, use_container_width=True)

    # Distribution of audio features for playlist
    st.markdown(
        """
    ---
    ### What is the audio feature distribution of the playlist?
    """
    )
    audio_feature_distributiuon_chart = get_audiofeature_distribution(
        music_df[audio_features]
    )
    st.altair_chart(audio_feature_distributiuon_chart, use_container_width=True)

    # Time based analysis
    top_tracks_df = get_top_tracks_df
    # TODO analysis

    #
    col1, _,_,_,_ = st.columns(5)
    range = col1.slider("Select the number of top songs to show", 1, 20, 10)
    stream_plotly = get_streaming_barplot(range=range)

    st.plotly_chart(stream_plotly, use_container_width=True)


# Path to the repo image folder
REPO_URL_ROOT = (
    "https://raw.githubusercontent.com/Strandgaard96/spotify-dashboard/master/"
)

# External files to download.
EXTERNAL_DEPENDENCIES = {}

if __name__ == "__main__":
    main()
