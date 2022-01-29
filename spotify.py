"""
Module responsible for handling spotify interaction.
"""
import numpy as np
import pandas as pd
import spotipy

# Not sure how this import will affect the app
import streamlit as st

from spotipy.oauth2 import SpotifyOAuth


# Inspiration taken from this:
# https://www.linkedin.com/pulse/extracting-your-fav-playlist-info-spotifys-api-samantha-jones/
def analyze_playlist(playlist_id, sp):
    """Get playlist data from given id and authentification manager

    Args:
        playlist_id (str): ID of playlist to get data for.
        sp (Spotify authentification instance): API authentification handler.

    Returns:
        playlist (DataFrame): Obtained playlist data.
        playlist_name (str): Name of playlist with the specified ID.
    """

    # Create empty dataframe with relevant columns
    playlist_features_list = [
        "artist",
        "genre",
        "album",
        "track_name",
        "track_id",
        "danceability",
        "energy",
        "key",
        "loudness",
        "mode",
        "speechiness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "duration_ms",
        "time_signature",
    ]
    playlist_df = pd.DataFrame(columns=playlist_features_list)

    # Get the number of tracks in the playlist
    playlist_length = sp.playlist(playlist_id)["tracks"]["total"]
    playlist_name = sp.playlist(playlist_id)["name"]

    # Create loop values based on playlist length
    offsets = np.arange(0, playlist_length + (100 - playlist_length % 100), 100)

    # Loop through every track in the playlist,
    # extract features and append the features to the playlist.
    for offset in offsets:
        playlist = sp.playlist_items(playlist_id=playlist_id, limit=100, offset=offset)[
            "items"
        ]
        for track in playlist:

            # Create empty dict for holding extracted features
            playlist_features = {}

            # Get metadata
            playlist_features["artist"] = track["track"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]
            playlist_features["track_id"] = track["track"]["id"]
            playlist_features["track_popularity"] = track["track"]["popularity"]
            playlist_features["added_at"] = track["added_at"]

            # Get audio features
            try:
                audio_features = sp.audio_features(playlist_features["track_id"])[0]
            except:
                print(
                    f'Error getting audio features for track: {playlist_features["track_name"]},\n'
                    f"likely not valid track_id"
                )
            for feature in playlist_features_list[5:]:
                if audio_features is None:
                    playlist_features[feature] = 0
                else:
                    playlist_features[feature] = audio_features[feature]

            # Get artist genre
            this_artist_id = track["track"]["artists"][0]["id"]
            if this_artist_id is None:
                this_genres = ["unknown"]
            else:
                try:
                    this_artist_info = sp.artist(this_artist_id)
                    this_genres = this_artist_info["genres"]
                except spotipy.SpotifyException as exception:
                    print(exception)
                    print(
                        f"Experienced an error when getting artist. Likely invalid artist id for the track: {track['track']['name']}"
                        f"The artist was : {track['track']['artists'][0]['name']}"
                    )
                    this_genres = []
                if not this_genres:
                    this_genres = ["unknown"]
            # Convert list of genres to string for storage in dataframe
            playlist_features["genre"] = "/".join(this_genres)

            # Concat the dfs
            track_df = pd.DataFrame(playlist_features, index=[0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    return playlist_df, playlist_name


def usage_analysis(sp, period="long_term"):
    """Get user top tracks and artists

    Args:
        sp: spotipy api handler.

    Returns:
        top_tracks_df (DataFrame):
    """

    # Create empty dataframe with relevant columns
    top_tracks_features_list = [
        "artist",
        "track_name",
        "popularity",
        "explicit",
    ]
    top_tracks_df = pd.DataFrame(columns=top_tracks_features_list)

    top_tracks = sp.current_user_top_tracks(time_range="short_term")
    total_top_tracks = top_tracks["total"]

    # Create loop values based on number of top tracks
    offsets = np.arange(0, total_top_tracks + (20 - total_top_tracks % 100), 20)

    for offset in offsets:
        top_tracks = sp.current_user_top_tracks(
            limit=20, offset=offset, time_range=period
        )["items"]
        for track in top_tracks:
            # Create empty dict for holding extracted features
            track_features = {}

            # TODO extract features
            track_features['artist'] = track["artists"][0]["name"]
            track_features['track_name'] = track["name"]
            track_features['popularity'] = track["popularity"]
            track_features['explicit'] = track["explicit"]
            # Concat the dfs
            track_df = pd.DataFrame(track_features, index=[0])
            top_tracks_df = pd.concat([top_tracks_df, track_df],ignore_index=True)

    return top_tracks_df


def spotify_driver(playlist_id=None):

    # Define the scope. You ensure that only a part of the information can be accessed.
    scope = "user-top-read"

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=st.secrets["CLIENT_ID"],
            client_secret=st.secrets["CLIENT_SECRET"],
            redirect_uri=st.secrets["REDIRECT_URI"],
            scope=scope,
        )
    )

    top_tracks_df = usage_analysis(sp=sp)

    # Define new scope for playlist analysis
    scope = "playlist-read-private"

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=st.secrets["CLIENT_ID"],
            client_secret=st.secrets["CLIENT_SECRET"],
            redirect_uri=st.secrets["REDIRECT_URI"],
            scope=scope,
        )
    )

    # Playlist id to download data for
    playlist_df, playlist_name = analyze_playlist(playlist_id=playlist_id, sp=sp)

    # Save dataframe
    playlist_df.to_csv(f"data/{playlist_name}.csv", index=False)


if __name__ == "__main__":
    playlist_id = "0mIif2dKh0Ns2RPd86w10l"
    spotify_driver(playlist_id=playlist_id)
