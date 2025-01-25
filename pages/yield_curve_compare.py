from datetime import date, timedelta
from pprint import pprint

import streamlit as st
import altair as alt
import pandas as pd
import math

from utils import TREASURY_SERIES, get_latest_yield_curve, update_csv_files


st.set_page_config(page_title="CMH Charts",
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="collapsed")


def yield_curve_chart():
    yield_curve1  = get_latest_yield_curve(date=st.session_state.date1)
    yield_curve2  = get_latest_yield_curve(date=st.session_state.date2)

    date1 = str(st.session_state.date1)
    date2 = str(st.session_state.date2)

    print(f'date 1: {date1}')
    pprint(yield_curve1)
    print(f'\ndate 2: {date2}')
    pprint(yield_curve2)

    yield_curve_df1 = pd.DataFrame(yield_curve1, columns=["duration", date1])
    yield_curve_df2 = pd.DataFrame(yield_curve2, columns=["duration", date2])

    # Round down to nearest 0.1
    y_min = math.floor(min(yield_curve_df1[date1]) * 10) / 10
    y_min = min(y_min, math.floor(min(yield_curve_df2[date2]) * 10) / 10)

    y_max = math.ceil(max(yield_curve_df1[date1]) * 10) / 10
    y_max = max(y_max, math.ceil(max(yield_curve_df2[date2]) * 10) / 10)

    # inner=intersection, outer=union
    combined_df = pd.merge(yield_curve_df1, yield_curve_df2, on="duration", how='inner')

    long_df = combined_df.melt(id_vars="duration", value_vars=[date1, date2],
                               var_name='Series', value_name='Yield')

    line_chart = alt.Chart(long_df).mark_line(interpolate="monotone", size=5).encode(
        x=alt.X("duration:O", title="Duration", sort=list(combined_df["duration"])),
        y=alt.Y("Yield:Q", title="Yield", scale=alt.Scale(domain=[y_min, y_max]), axis=alt.Axis(orient="left")),
        color=alt.Color("Series:N", title=None,
                        scale=alt.Scale(
                            domain=[date1, date2],
                            range=["steelblue", "#a94442"]
                        ),
                        legend=alt.Legend(
                            orient="bottom",
                            titleOrient="left",
                            symbolStrokeWidth=20,
                            symbolSize=10000,
                            labelFontSize=20,
                            padding=-25,                            
                        )
        )
    ).properties(
        width=700,
        height=600,
    ).interactive()

    points1 = alt.Chart(yield_curve_df1).mark_point(filled=True, size=75).encode(
        x=alt.X("duration:O", sort=list(yield_curve_df1["duration"])),  # Same x encoding as the line
        y=alt.Y(f"{date1}:Q", axis=alt.Axis(orient="right", title=None))                                           # Same y encoding as the line
    )

    points2 = alt.Chart(yield_curve_df2).mark_point(filled=True, size=75).encode(
        x=alt.X("duration:O", sort=list(yield_curve_df1["duration"])),
        y=alt.Y(f"{date2}:Q", axis=alt.Axis(orient="right", title=None)),
        color=alt.value("#a94442")
    )

    layered_chart = alt.layer(
        line_chart,
        points1,
        points2,
    ).interactive()
 
    st.altair_chart(layered_chart, use_container_width=True)

    # legend_col1, legend_col2  = st.columns([1, 1])

    # with legend_col1:
    #     st.info(str(st.session_state.date1))
    # with legend_col2:
    #     st.error(str(st.session_state.date2))


# def yield_curve_chart():
#     yield_curve1  = get_latest_yield_curve(date=st.session_state.date1)
#     yield_curve2  = get_latest_yield_curve(date=st.session_state.date2)

#     print(f'date1: {st.session_state.date1}')
#     print(yield_curve1)
#     print(f'\ndate2: {st.session_state.date2}')
#     print(yield_curve2)

#     print(type(yield_curve1))

#     yield_curve_df1 = pd.DataFrame(yield_curve1, columns=["x", "y1"])
#     yield_curve_df2 = pd.DataFrame(yield_curve2, columns=["x", "y2"])

#     y_min = math.floor(min(yield_curve_df1["y1"]) * 10) / 10  # Round down to nearest 0.1
#     y_min = min(y_min, math.floor(min(yield_curve_df2["y2"]) * 10) / 10)

#     y_max = math.ceil(max(yield_curve_df1["y1"]) * 10) / 10
#     y_max = max(y_max, math.ceil(max(yield_curve_df2["y2"]) * 10) / 10)

#     # TODO: tooltip --> add line's date
#     # TODO: for legend displaying dates, use concat instead of creating 2 alt.Charts
#     combined_df = pd.concat([yield_curve_df1, yield_curve_df2], axis=1, join='inner')
#     print(combined_df.tail())
#     print("----")
#     print(yield_curve_df1.tail())
#     # inner=intersection, outer=union
#     #combined_df = pd.concat([yield_curve_df1, yield_curve_df2], ignore_index=True)
#     #print(combined_df.info())
#     #print(combined_df.tail())
#     combined_df2 = pd.merge(yield_curve_df1, yield_curve_df2, on='x', how='inner')
#     print(combined_df2.tail())

#     line = alt.Chart(yield_curve_df1).mark_line(interpolate="monotone").encode(
#         x=alt.X("x:O", title="Duration", sort=list(yield_curve_df1["x"])),  # 'O' specifies an ordinal scale for x-axis
#         y=alt.Y("y1:Q", title="Yield", scale=alt.Scale(domain=[y_min, y_max])) # 'Q' specifies a quantitative scale for y-axis
#         #color=alt.Color('legend_label:N', title="Legend")
#         #tooltip=[alt.Tooltip(title="date 1")]
#         #xtooltip=["x:T", "y:Q"]
#     ).properties(
#         width=700,
#         height=600,
#     )

#     points = alt.Chart(yield_curve_df1).mark_point(filled=True, size=50).encode(
#         x=alt.X("x:O", sort=list(yield_curve_df1["x"])),  # Same x encoding as the line
#         y=alt.Y("y1:Q")                      # Same y encoding as the line
#     )

#     line_2 = alt.Chart(yield_curve_df2).mark_line(interpolate="monotone").encode(
#         x=alt.X("x:O", sort=list(yield_curve_df2["x"])),
#         y=alt.Y("y2:Q", scale=alt.Scale(domain=[y_min, y_max])),
#         color=alt.value("red"),  # Color for the second dataset
#     )

#     points_2 = alt.Chart(yield_curve_df2).mark_point(filled=True, size=50).encode(
#         x=alt.X("x:O", sort=list(yield_curve_df2["x"])),
#         y=alt.Y("y2:Q"),
#         color=alt.value("red")  # Color for the second dataset
#     )

#     # chart = (line + points + line_2 + points_2).properties(
#     #     title="Yield Curve Comparison"
#     # )

#     layered_chart = alt.layer(
#         line,
#         line_2,
#         points,
#         points_2
#     ).interactive()

#     st.altair_chart(layered_chart, use_container_width=True)

#     #st.text("date 1, date 2")

#     legend_col1, legend_col2  = st.columns([1, 1])

#     with legend_col1:
#         st.info(str(st.session_state.date1))
#     with legend_col2:
#         st.error(str(st.session_state.date2))


def date_selction():
    start_date_col, end_date_col  = st.columns([1, 1])

    with start_date_col:
        st.session_state.date1 = st.date_input("Date 1", date.today()-timedelta(days=7), key="selected_start_date", min_value=date(1976,6,1), max_value="today")
    with end_date_col:
        st.session_state.date2 = st.date_input("Date 2", date.today(), key="selected_end_date", min_value=date(1976,6,1), max_value="today")


def main():
    st.header("Yield Curve Comparison")

    date_selction()
    yield_curve_chart()


if 'init' not in st.session_state:
    update_csv_files()
    st.session_state.init = True

    st.session_state.date1 = date.today() - timedelta(days=7)
    st.session_state.date2 = date.today()


if __name__ == "__main__":
    main()