import streamlit as st

from data import get_comic
from plotting import (get_most_played_animation, get_streaming_barplot,
                      get_temporal_distribution)
from streaming_data import get_streaming_df

# For getting png image from remote


st.set_page_config(page_title="Streaming", layout="wide", page_icon=":fire:")
# Hack to try and center image.
_, col2, _ = st.sidebar.columns([1, 1, 1])
# Sombra logo in sidebar
col2.image("images/sombra.png", width=110)
# What to put under the sidebar
st.sidebar.markdown(
    '<h4>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png"\
     alt="Streamlit logo" \
     height="16">&nbsp by <a href="https://github.com/Strandgaard96">Strandgaard96</a></h4>',
    unsafe_allow_html=True,
)


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

df = get_streaming_df()
# Copy to be able to change the df. The original df is cached.
streaming_df = df.copy()

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
# Most played as function of year
I am questioning how useful this visualization is, but i made so here it is. 
"""
)

plotly_most_played_animated = get_most_played_animation(streaming_df=streaming_df)
st.plotly_chart(plotly_most_played_animated, use_container_width=True)




st.markdown(
    """
---
### Congratz, you made it to the end. Thanks for checking out my random random data. Heres a comic :tiger:. 
"""
)

img = get_comic()
st.image(img, caption="Current comic from xkcd")
