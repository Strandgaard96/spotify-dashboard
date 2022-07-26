import datetime as dt

import altair as alt
import plotly.figure_factory as ff
from plotly import express as px
from plotly.subplots import make_subplots


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
        .configure_axis(labelFontSize=20, titleFontSize=20, labelAngle=-45)
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


def get_audiofeature_distribution(df, **plt_kwargs):

    # Old plot code using altar
    # chart = (
    #    alt.Chart(data)
    #    .transform_fold(data.columns.tolist(), as_=["Audio feature", "value"])
    #    .transform_density(
    #        density="value",
    #        bandwidth=0.05,
    #        groupby=["Audio feature"],
    #        extent=[0, 1],
    #        counts=True,
    #        steps=500,
    #    )
    #    .mark_area(opacity=0.7)
    #    .encode(alt.X("value:Q"), alt.Y("density:Q"), alt.Color("Audio feature:N"))
    #    .properties(width=400, height=400)
    # )

    # New plot using plotly
    fig = ff.create_distplot(
        [df[c] for c in df.columns],
        df.columns,
        bin_size=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
    )
    fig.update_layout(
        title_text="Audio feature KDE plot", width=700, height=700, font=dict(size=16)
    )

    return fig


def get_temporal_distribution(df, time_range=None,season=None, **plt_kwargs):

    # Restrict song name length by skipping possible feature statements in parenthesis
    df["trackName"] = df["trackName"].str.split("(", expand=True)[0]

    fig = make_subplots(
        rows=3,
        cols=3,
        shared_yaxes=True,
        subplot_titles=(
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ),
    )

    row = 0
    col = 0

    mask = (df["endTime"] > time_range[0]) & (df["endTime"] <= time_range[1])
    df = df.loc[mask]

    seasons = {'Winter':(12,1,2),'Summer':(6,7,8),'Spring':(3,4,5),'Autumn':(9,10,11)}

    # Limit to chosen seaon
    if season:
        df = getMonths(df,*seasons[season])

    for i in range(7):

        if i % 3 == 0:
            row += 1
        col = col % 3 + 1

        day = df[df["endTime"].dt.dayofweek == i]
        count = day.groupby(["trackName", "artistName"], as_index=False).size()
        sorted_count = count.sort_values(by="size", ascending=False)

        temp_fig = px.bar(
            sorted_count[0:5],
            x="trackName",
            y="size",
            hover_data=["trackName", "artistName"],
            color="size",
            labels={"size": "Plays", "trackName": "Track name"},
            height=600,
        )
        fig.add_trace(temp_fig.data[0], row=row, col=col)

    fig.update_layout(font=dict(size=16), showlegend=False, height=800)

    # options
    # coloraxis=dict(colorscale='Bluered_r'),
    # fig.show()

    return fig

def getMonths(input, m1, m2, m3):
    return input.loc[(input.endTime.dt.month==m1) | (input.endTime.dt.month==m2) | (input.endTime.dt.month==m3)]

def get_streaming_barplot(df=None, range=10, time_range=None):

    mask = (df["endTime"] > time_range[0]) & (df["endTime"] <= time_range[1])

    df["trackName"] = df["trackName"].str.split("(", expand=True)[0]
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
        height=600,
    )
    fig.update_layout(font=dict(size=16))
    # Here are two ways of showing the figure
    # show(fig)
    # fig.show()
    return fig
def get_most_played_animation(streaming_df = None):

    df = streaming_df.groupby([(streaming_df.endTime.dt.year), (streaming_df.trackName)]) \
        .agg({'ms_played': 'sum', 'trackName': 'count', 'artistName': 'first'}).rename(
        columns={'trackName': 'count'}).reset_index()
    df = df.groupby(['endTime']).apply(lambda x: x.nlargest(100, ['count'])).reset_index(drop=True)

    fig = px.scatter(df, x="ms_played", y="count", animation_frame="endTime",
               size='ms_played', hover_name="trackName", hover_data={'artistName': True},
               log_x=True, size_max=60, range_y=[0, 200], range_x=[10000, 25000000])

    fig.update_layout(font=dict(size=16), showlegend=False, height=600)

    return fig