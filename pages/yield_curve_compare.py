from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint

import streamlit as st
import altair as alt
import pandas as pd
import math

from utils import TREASURY_SERIES, get_dated_yield_curve, update_csv_files, get_latest_data_date


st.set_page_config(page_title="CMH Charts",
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="collapsed")


# TODO: dates that are missing duration data( 1-month, 2000)
def yield_curve_chart():
    yield_curve1, date1 = get_dated_yield_curve(st.session_state.date1)
    if date1 == str(st.session_state.date2):
        yield_curve2, date2 = get_dated_yield_curve(st.session_state.date2 - timedelta(days=1))
    else:
        yield_curve2, date2 = get_dated_yield_curve(st.session_state.date2)

    if date1 == date2:
        if st.session_state.date2.weekday() in (5, 6):
            st.error("Date selection error: do not select weekends / non trading days")
            return
        st.error("Dates cannot match")
        return

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
                            orient="top",
                            titleOrient="left",
                            symbolStrokeWidth=20,
                            symbolSize=10000,
                            labelFontSize=20,
                            padding=0,                            
                        )
        )
    ).properties(
        width=700,
        height=600,
    ).interactive()

    points1 = alt.Chart(yield_curve_df1).mark_point(filled=True, size=75).encode(
        x=alt.X("duration:O", sort=list(yield_curve_df1["duration"])), # Same x encoding as the line
        y=alt.Y(f"{date1}:Q", axis=alt.Axis(orient="right", title=None)) # Same y encoding as the line
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


def update_data_button():
    latest_data_date = st.session_state.latest_data_date.strftime("%Y-%m-%d")
    st.write(f"Latest data from {latest_data_date}")

    if st.session_state.display_data_update_btn:

        download_data_btn = st.button("Download latest data")
        if download_data_btn:
            print('downloading')
            update_csv_files(days_until_stale=1)
            st.session_state.display_data_update_btn = False


def date_selction():
    start_date_col, end_date_col  = st.columns([1, 1])

    # TODO: max_values need to be lateset data date?, not today's date
    with start_date_col:
        st.session_state.date1 = st.date_input("Date 1", date.today()-timedelta(days=7), key="selected_start_date", min_value=date(1976,6,1), max_value=st.session_state.latest_data_date)
    with end_date_col:
        st.session_state.date2 = st.date_input("Date 2", st.session_state.latest_data_date, key="selected_end_date", min_value=date(1976,6,1), max_value=st.session_state.latest_data_date)


def date_differnce():
    diff = relativedelta(st.session_state.date1, st.session_state.date2)

    res_str = "Date Difference: "
    if diff.years:
        res_str += f"{abs(diff.years)} years, "
    if diff.months:
        res_str += f"{abs(diff.months)} months, "
    
    res_str += f"{abs(diff.days)} days"
    return res_str


def main():
    st.header("Yield Curve Comparison")

    update_data_button()

    date_selction()
    st.write(date_differnce())
    
    yield_curve_chart()


if 'init_yc' not in st.session_state:
    update_csv_files()
    st.session_state.init_yc = True

    st.session_state.latest_data_date = get_latest_data_date()

    st.session_state.date1 = date.today() - timedelta(days=7)
    st.session_state.date2 = date.today()

    st.session_state.display_data_update_btn = True


if __name__ == "__main__":
    main()