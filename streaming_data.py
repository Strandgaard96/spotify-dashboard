import json
import numpy as np
import pandas as pd
from glob import glob
from pathlib import Path

def main():

    path = Path('data/MyData').rglob('*History*.json')
    stream_df = pd.concat((pd.read_json(f, convert_dates=['endTime']) for f in path))
    stream_df.to_csv('data/streaming_data.csv')

    path = Path('data/playlists').rglob('*.csv')
    playlist_df = pd.concat((pd.read_csv(f) for f in path))

    stream_df.rename(columns={"trackName": "track_name"},inplace=True)

    total = pd.merge(stream_df, playlist_df, on='track_name')

    return stream_df


if __name__ == '__main__':
    main()