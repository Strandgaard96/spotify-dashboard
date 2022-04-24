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

    path = Path("data/MyData").rglob("*History*.json")
    stream_df = pd.concat((pd.read_json(f, convert_dates=["endTime"]) for f in path))
    stream_df.to_csv("data/streaming_data.csv")

    path = Path("data/playlists").rglob("*.csv")
    playlist_df = pd.concat((pd.read_csv(f) for f in path))

    stream_df.rename(columns={"trackName": "track_name"}, inplace=True)

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
        height=400,
    )
    fig.update_layout(font=dict(size=16))
    # Here are two ways of showing the figure
    # show(fig)
    # fig.show()
    return fig


if __name__ == "__main__":
    plot_bar()
    # get_stream_df()
