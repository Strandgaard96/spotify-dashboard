import pandas as pd
from pathlib import Path


def get_stream_df():

    path = Path("data/TOTALSTREAM").rglob("*endsong*.json")
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


if __name__ == "__main__":

    # Debugging stuff
    # df = pd.read_csv("data/total_streaming_data.csv", parse_dates=["endTime"])

    # sorted_df = df.sort_values(by="endTime", ascending=True)
    # one = sorted_df["endTime"].iloc[0]
    # two = sorted_df["endTime"].iloc[-1]

    # get_streaming_barplot(df, time_range=(one, two), range=50)
    get_stream_df()
