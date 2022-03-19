import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image


@st.cache
def get_wordcloud_image(playlist_name=None):
    """Get wordcloud image from repo (which is cached by streamlit decorator)"""
    image = Image.open(f"data/{playlist_name}.png")
    return image


# domain=None, title=None
def get_altair_histogram(data=None, genre_artists_count=None, **plt_kwargs):
    """Create altair chart object

    Args:
        data (DataFrame): Contains genres and the counts of each genre
        Also an artist column should be present for tooltip.
        genre_artists_count (dict): Contains Counter iterable with artists for each genre
    Returns:
        hist (altair chart): Altair chart object
    """

    def _applyfunc(genre, artists):
        "Helper func to convert artist column format to tooltip suitable string"

        # How many artists to include in tooltip is given by num
        # 5 is default
        num = 5

        # Handle if there are less than 5 top artists for genre
        if len(artists) < 5:
            num = len(artists)

        # Generate tooltip string.
        # TODO handle the last dash in a better way
        top_artists = ""
        for i in range(num):
            top_artists += (
                f"{artists[i]}({genre_artists_count[genre][artists[i]]})\n - "
            )
        return top_artists[0:-2]

    # Create buffer to hold formated data
    buffer = data.copy()

    # Format the top five artists of a genre to be shown in tooltip
    buffer["artists"] = data[["artists", "genre"]].apply(
        lambda row: _applyfunc(row["genre"], row["artists"]), axis=1
    )

    # Old version
    # data['artists'] = data['artists'].map(lambda x: f" - ".join(x[0:5]))

    hist = (
        alt.Chart(buffer)
        .mark_bar()
        .encode(
            x=alt.X(
                "genre",
                axis=alt.Axis(title="Genre"),
                sort=alt.EncodingSortField(order="ascending"),
            ),
            y=alt.Y(
                "count",
                axis=alt.Axis(title="Counts", tickMinStep=1),
                scale=alt.Scale(domain=plt_kwargs.get("domain", [0, 1])),
            ),
            color=alt.Color("genre", legend=None),
            tooltip=alt.Tooltip("artists", title="title"),
        )
        .properties(
            width=200, height=500, title=plt_kwargs.get("title", "Genre histogram")
        )
        .configure_axis(labelFontSize=16, titleFontSize=16, labelAngle=-45)
        .configure_title(
            fontSize=20,
        )
    )
    # Can be added to enable scroll and zoom in the chart
    # .interactive()

    return hist


def get_audiofeature_chart(data, **plt_kwargs):
    """Plot audio features area plot

    Args:
        data (DataFrame): Contains audio feature data

    Returns:
        chart_features (altair chart): Chart object to show in main page
    """
    chart_features = (
        alt.Chart(data)
        .mark_area(opacity=0.3)
        .encode(
            x="Feature",
            y=alt.Y("Value", stack=None, scale=alt.Scale(domain=[0, 1])),
            color="Song",
        )
        .configure_axis(labelFontSize=16, titleFontSize=16, labelAngle=-45)
        .properties(title="Audio features", height=500, width=200)
        .configure_title(
            fontSize=20,
        )
        .configure_legend(symbolSize=250, titleFontSize=25, labelFontSize=25)
    )
    return chart_features


def get_audiofeature_distribution(data, **plt_kwargs):

    chart = (
        alt.Chart(data)
        .transform_fold(data.columns.tolist(), as_=["Audio feature", "value"])
        .transform_density(
            density="value",
            bandwidth=0.1,
            groupby=["Audio feature"],
            extent=[0, 1],
            counts=True,
            steps=500,
        )
        .mark_area(opacity=0.7)
        .encode(alt.X("value:Q"), alt.Y("density:Q"), alt.Color("Audio feature:N"))
        .properties(width=400, height=400)
    )

    return chart
