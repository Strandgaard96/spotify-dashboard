import pandas as pd
import spotipy
import streamlit as st
from spotipy import SpotifyOAuth

from spotify import spotify_driver


@st.cache
def load_metadata(url):
    return pd.read_csv(url)


@st.cache
def get_playlist_df(data):

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


@st.cache
def get_top_tracks_df(data):

    # Define the dtypes for columns to ensure correct format for later analysis
    dtypes = {
        "artist": "str",
        "track_name": "str",
        "popularity": "int",
        "explicit": "bool",
    }
    df = pd.read_csv(data, dtype=dtypes)
    return df.set_index("track_name")


def aquire_data_app():
    """Streamlit page for aquiring new playlist data

    Args:

    Returns:

    """
    scope = "playlist-read-private"
    st.title("Download data page")
    st.markdown(
        """
        Here you can enter a playlist id to download playlist data to analyze
        """
    )

    placeholder = st.empty()
    playlist_id = placeholder.text_input("Please enter a valid playlist id")
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=st.secrets["CLIENT_ID"],
                client_secret=st.secrets["CLIENT_SECRET"],
                redirect_uri=st.secrets["REDIRECT_URI"],
                scope=scope,
            )
        )
        playlist_name = sp.playlist(playlist_id)["name"]
    except spotipy.SpotifyException as exception:
        st.error("Please enter a valid playlist id")
    else:
        success = st.success(
            f"Found playlist with name: {playlist_name}\n" f" Retrieving playlist data"
        )
        with st.spinner("Please wait while data is downloading"):
            spotify_driver(playlist_id=playlist_id)
        success.empty()
        placeholder.empty()
        st.success(
            f"Finished downloading data. Please select the dataset in the dropdown and run the app."
        )
    return None
