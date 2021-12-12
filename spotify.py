import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import config


# Inspiration taken from this: https://www.linkedin.com/pulse/extracting-your-fav-playlist-info-spotifys-api-samantha-jones/
def analyze_playlist(creator, playlist_id, sp):
    # Create empty dataframe
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

    # Create empty dict
    playlist_features = {}

    # Get the number of tracks in the playlist
    playlist_length = sp.playlist(playlist_id)["tracks"]["total"]
    # Create loop values based on playlist length
    offsets = np.arange(0, playlist_length + (100 - playlist_length % 100), 100)

    # Loop through every track in the playlist, extract features and append the features to the playlist d
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
                playlist_features[feature] = audio_features[feature]

            # Get artist genre
            thisArtistId = track["track"]["artists"][0]["id"]
            if thisArtistId == None:
                thisGenres = "[unknown]"
            else:
                try:
                    thisArtistInfo = sp.artist(thisArtistId)
                    thisGenres = thisArtistInfo["genres"]
                except:
                    thisGenres = []
                if thisGenres == []:
                    thisGenres = ['unknown']
            playlist_features["genre"] = '/'.join(thisGenres)

            # To get the top artists, the scope need changing :
            # https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-read-private
            # sp.current_user_top_artists()

            # Concat the dfs
            track_df = pd.DataFrame(playlist_features, index=[0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

    return playlist_df


def main():

    # Define the scope. U ensure that only a part of the information can be accessed.
    scope = "playlist-read-private"

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            redirect_uri=config.REDIRECT_URI,
            scope=scope,
        )
    )

    playlist_id = "3PDP5gjPxjiXfYbgf8ll9C"
    playlist_df = analyze_playlist(creator="dansken02", playlist_id=playlist_id, sp=sp)
    playlist_df.to_csv("data/$.csv", index=False)


if __name__ == "__main__":
    main()
