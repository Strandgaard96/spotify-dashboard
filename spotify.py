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
def analyze_playlist(creator, playlist_id, sp):
    """
    Extract relevant track data for given playlist id
    :param creator: str
    :param playlist_id : str
    :param sp: Spotify authentification manager : class
    :return: playlist : DataFrame
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

    # Create empty dict for holding extracted features
    playlist_features = {}

    # Get the number of tracks in the playlist
    playlist_length = sp.playlist(playlist_id)["tracks"]["total"]
    # Create loop values based on playlist length
    offsets = np.arange(0, playlist_length + (100 - playlist_length % 100), 100)

    # Loop through every track in the playlist,
    # extract features and append the features to the playlist.
    for offset in offsets:
        playlist = sp.user_playlist_tracks(
            creator, playlist_id=playlist_id, limit="100", offset=offset
        )["items"]
        for track in playlist:

            # Get metadata
            playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]
            playlist_features["track_id"] = track["track"]["id"]
            playlist_features["track_popularity"] = track["track"]["popularity"]
            playlist_features["added_at"] = track["added_at"]
            # Get audio features
            audio_features = sp.audio_features(playlist_features["track_id"])[0]
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

            # To get the top artists, the scope need changing :
            # https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-read-private
            # sp.current_user_top_artists()

            # Concat the dfs
            track_df = pd.DataFrame(playlist_features, index=[0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    # Get playlist name to return
    playlist_name = sp.user_playlist(
        creator, playlist_id=playlist_id)['name']

    return playlist_df, playlist_name


def main():

    # Define the scope. U ensure that only a part of the information can be accessed.
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
    playlist_id = "3vmJSGD3GyrWBdTrpNazPs"
    playlist_df, playlist_name = analyze_playlist(creator="dansken02", playlist_id=playlist_id, sp=sp)

    # Save dataframe
    playlist_df.to_csv(f"data/{playlist_name}.csv", index=False)


if __name__ == "__main__":
    main()
