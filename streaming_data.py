import json
import numpy as np
import pandas as pd



def main():

    dtypes = {
        "endTime": "datetime",
        "artistName": "str",
        "trackName": "str",
        "msPlayed": "int",
    }
    df1 = pd.read_json(f'data/MyData/StreamingHistory{0}.json',dtype=dtypes)
    df2 = pd.read_json(f'data/MyData/StreamingHistory{1}.json', dtype=dtypes)
    df3 = pd.read_json(f'data/MyData/StreamingHistory{2}.json', dtype=dtypes)
    df4 = pd.read_json(f'data/MyData/StreamingHistory{3}.json', dtype=dtypes)
    df5 = pd.read_json(f'data/MyData/StreamingHistory{4}.json', dtype=dtypes)

    stream_df= pd.concat([df2,df2,df3,df4,df5])
    stream_df.to_csv('data/streaming_data.csv')

    return stream_df




if __name__ == '__main__':
    main()