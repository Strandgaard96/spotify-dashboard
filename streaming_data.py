import json
import numpy as np
import pandas as pd
from glob import glob
from pathlib import Path
import plotly.graph_objects as go
from plotly.io import show
import plotly.express as px
import plotly.figure_factory as ff


def get_stream_df():

    path = Path("data/TOTALSTREAM").rglob("*endsong*.json")
    stream_df = pd.concat((pd.read_json(f, convert_dates=["ts"]) for f in path))

    stream_df.rename(columns={"ts": "endTime", "master_metadata_track_name": "trackName",
                       "master_metadata_album_artist_name": "artistName"}, inplace=True)
    stream_df.to_csv("data/total_streaming_data.csv")

    path = Path("data/playlists").rglob("*.csv")
    playlist_df = pd.concat((pd.read_csv(f) for f in path))

    #stream_df.rename(columns={"trackName": "track_name"}, inplace=True)

    # total = pd.merge(stream_df, playlist_df, on='track_name')

    return stream_df


def get_streaming_barplot(df=None, range=10, time_range=None):

    mask = (df["endTime"] > time_range[0]) & (df["endTime"] <= time_range[1])
    new_df = df.loc[mask]

    count = new_df.groupby(["trackName", "artistName"], as_index=False).size()
    sorted_count = count.sort_values(by="size", ascending=False)

    fig = px.bar(
        sorted_count[0:range],
        x="trackName",
        y="size",
        hover_data=["trackName", "artistName"],
        color="size",
        labels={"size": "Plays", "trackName": "Track Name"},
        height=800,
    )
    fig.update_layout(font=dict(size=16))
    # Here are two ways of showing the figure
    # show(fig)
    fig.show()
    return fig


if __name__ == "__main__":


    df = pd.read_csv('data/total_streaming_data.csv',parse_dates=["endTime"])

    sorted_df=df.sort_values(by='endTime', ascending=True)
    one = sorted_df['endTime'].iloc[0]
    two = sorted_df['endTime'].iloc[-1]

    get_streaming_barplot(df, time_range=(one, two), range=50)
    #get_stream_df()