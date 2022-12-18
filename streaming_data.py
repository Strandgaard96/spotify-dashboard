import io
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


def convert_stream_data():

    path = Path("data/MyData").rglob("*endsong*.json")
    stream_df = pd.concat((pd.read_json(f, convert_dates=["ts"]) for f in path))

    stream_df.rename(
        columns={
            "ts": "endTime",
            "master_metadata_track_name": "trackName",
            "master_metadata_album_artist_name": "artistName",
            "master_metadata_album_album_name": "albumName",
        },
        inplace=True,
    )

    # Select only non_sensitive data to upload
    stream_df = stream_df[
        [
            "endTime",
            "ms_played",
            "trackName",
            "artistName",
            "reason_start",
            "reason_end",
            "shuffle",
            "skipped",
        ]
    ]

    stream_df.to_csv("data/total_streaming_data.csv")

    path = Path("data/playlists").rglob("*.csv")
    playlist_df = pd.concat((pd.read_csv(f) for f in path))

    # stream_df.rename(columns={"trackName": "track_name"}, inplace=True)
    # total = pd.merge(stream_df, playlist_df, on='track_name')

    return stream_df


@st.cache
def get_streaming_df():
    data = Path("data/total_streaming_data.csv")
    if data.is_file():
        dtypes = {
            "ms_played": "int",
            "trackName": "str",
            "artistName": "str",
            "reason_start": "str",
            "reason_end": "str",
            "shuffle": "bool",
            "skipped": "float",
        }
        df = pd.read_csv(
            "data/total_streaming_data.csv", parse_dates=["endTime"], dtype=dtypes
        )
    else:
        print("Data not available. Using small dataset instead")
        df = pd.read_csv("data/streaming_data.csv", parse_dates=["endTime"])
    return df


st.cache
def get_streaming_df_remote():
    dtypes = {
        "ms_played": "int",
        "trackName": "str",
        "artistName": "str",
        "reason_start": "str",
        "reason_end": "str",
        "shuffle": "bool",
        "skipped": "float",
    }

    # Username of your GitHub account

    username = "Strandgaard96"

    # Personal Access Token (PAO) from your GitHub account

    token = st.secrets["GITHUB_TOKEN"]

    # Creates a re-usable session object with your creds in-built
    github_session = requests.Session()
    github_session.auth = (username, token)

    # Downloading the csv file from your GitHub
    url = "https://raw.githubusercontent.com/Strandgaard96/data_files/master/total_streaming_data.csv"  # Make sure the url is the raw version of the file on GitHub
    download = github_session.get(url).content


    # Reading the downloaded content and making it a pandas dataframe
    df = pd.read_csv(
        io.StringIO(download.decode("utf-8")), dtype=dtypes
    )

    df["endTime"] = df["endTime"].apply(pd.to_datetime)

    return df


if __name__ == "__main__":

    df = get_streaming_df_remote()
    print("lol")
    # Debugging stuff
    # df = pd.read_csv("data/total_streaming_data.csv", parse_dates=["endTime"])

    # sorted_df = df.sort_values(by="endTime", ascending=True)
    # one = sorted_df["endTime"].iloc[0]
    # two = sorted_df["endTime"].iloc[-1]

    # get_streaming_barplot(df, time_range=(one, two), range=50)
    convert_stream_data()
