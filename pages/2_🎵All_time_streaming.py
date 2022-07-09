import streamlit as st
import pandas as pd
from data import (
    download_file,
    get_genre_count,
    generate_wordcloud,
    get_file_content_as_string,
)
from plotting import (
    get_temporal_distribution,
    get_streaming_barplot,
)

# For getting png image from remote
from PIL import Image
from io import BytesIO
from random import randint
import urllib.request
import requests
import json

st.set_page_config(page_title="Streaming", layout="wide", page_icon=":fire:")

# Streaming analysis
st.markdown(
    """
---
# All-time spotify streaming analysis :musical_note:
This section contains visualizations and analysis of my total spotify usage, from my first streams in 2010 to
today.
First, a simple overview of my most streamed songs in a given time period:



Select the number of songs to show and a time range.
"""
)
try:
    dtypes = {
        "ms_played": "int",
        "trackName": "str",
        "artistName": "str",
        "reason_start": "str",
        "reason_end": "str",
        "shuffle": "bool",
        "skipped": "float",
    }
    streaming_df = pd.read_csv(
        "data/total_streaming_data.csv", parse_dates=["endTime"], dtype=dtypes
    )
except FileNotFoundError:
    print("Data not available. Using small dataset instead")
    streaming_df = pd.read_csv("data/streaming_data.csv", parse_dates=["endTime"])
# Get the time range of the data
start_date = streaming_df["endTime"].min()
end_date = streaming_df["endTime"].max()

col1, col2, col3, _, _ = st.columns(5)
range = col1.slider(
    "Select the number of top songs to show", 1, 40, 10, key="slice_songs"
)
time_range1 = col2.slider(
    "Select start-date",
    min_value=start_date,
    max_value=end_date,
    value=start_date.to_pydatetime(),
    format="DD/MM/YY",
)
time_range2 = col3.slider(
    "Select end-date",
    min_value=start_date,
    max_value=end_date,
    value=end_date.to_pydatetime(),
    format="DD/MM/YY",
)

stream_plotly = get_streaming_barplot(
    df=streaming_df, range=range, time_range=(time_range1, time_range2)
)
st.plotly_chart(stream_plotly, use_container_width=True)

st.markdown(
    """
---
# Time based analysis :sunny: :cloud: :snowman: :umbrella:
How did my listening evolve over the weaks/years/seasons?
"""
)

st.markdown("What is my all-time most listened monday song?!")

col1, col2, col3, _, _ = st.columns(5)
time_range3 = col2.slider(
    "Select start-date",
    min_value=start_date,
    max_value=end_date,
    value=start_date.to_pydatetime(),
    format="DD/MM/YY",
    key="start",
)
time_range4 = col3.slider(
    "Select end-date",
    min_value=start_date,
    max_value=end_date,
    value=end_date.to_pydatetime(),
    format="DD/MM/YY",
    key="end",
)
temporal_plotly = get_temporal_distribution(
    df=streaming_df, time_range=(time_range3, time_range4)
)

st.plotly_chart(temporal_plotly, use_container_width=True)

st.markdown(
    """
---
### Congratz, you made it to the end. Thanks for checking out my random random data. Heres a comic :tiger:. 
"""
)

try:
    with requests.Session() as s:
        content = s.get("https://xkcd.com/info.0.json").content.decode()
        data = json.loads(content)
        HighestNumber = data["num"]

        random = True
        if random:
            rand_digits = randint(1, HighestNumber)
            endpoint = "https://xkcd.com/{}/info.0.json".format(rand_digits)
            content = s.get(endpoint).content.decode()
            data = json.loads(content)
            res = s.get(data["img"])
            img = Image.open(BytesIO(res.content))
        else:
            res = s.get(data["img"])
            img = Image.open(BytesIO(res.content))
except requests.ConnectionError:
    img = Image.open("data/comic.png")
    # error_image = Image.open("assets/xkcd_404.jpg")
    # error_image.show()

st.image(img, caption="Current comic from xkcd")

# What to put under the sidebar
st.sidebar.markdown(
    '<h4>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png"\
     alt="Streamlit logo" \
     height="16">&nbsp by <a href="https://github.com/Strandgaard96">Strandgaard96</a></h4>',
    unsafe_allow_html=True,
)
