import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from utils import (create_dataframes, lowest_yield_dataframe, highest_yield_dataframe,
                   fed_funds_rate_dataframe, create_yield_differential_dataframe,
                   RECESSIONS, RECESSION_ENDS, SP_500_PEAKS)

DATA_CSV = "data.csv"


def maturity_yield_time_series_chart():
    rate_data = create_dataframes(fillna=True)

    renamed_dfs = []
    for duration, df in rate_data.items():
        # Make a copy to avoid modifying the original
        df_copy = df.copy()

        # If your date column isn't already the index, set it as the index.
        # For example: df_copy.set_index("Date", inplace=True)
        # Also parse dates if needed.

        # Rename 'Close' (or whichever price column you have) to the stock name
        df_copy.rename(columns={"Close": duration}, inplace=True)

        renamed_dfs.append(df_copy)

    
    # Step 2: Combine the renamed DataFrames on their Date index
    # 'outer' join will include all dates present in any DataFrame
    combined_df = pd.concat(renamed_dfs, axis=1, join="outer")

    # Step 3: Plot the combined DataFrame
    st.title("Treasury rates")
    st.line_chart(combined_df)


def lowest_yielding_duration_time_series_chart_OLD(sample_rate="W", start_date="1965-01-01"):
    #TODO: add lowest interest rate
    lowest_yield_data = lowest_yield_dataframe(sample_rate=sample_rate)

    # Convert to Altair-friendly format
    #df_rate = lowest_yield_data.reset_index(drop=True)
    df_rate = lowest_yield_data.reset_index()

    df_rate = df_rate[df_rate["observation_date"] >= start_date]

    df_fed_funds = fed_funds_rate_dataframe(start_date=start_date).reset_index()

    # print("RATES COLS", df_rate.columns)
    # print("FF COLS", df_fed_funds.columns)

    df_rate['Category'] = 'Lowest Yielding Maturity'
    df_fed_funds['Category'] = 'Fed Funds Rate'

    # Combine the DataFrames into a single DataFrame 
    #df_alt = pd.concat([df_rate, df_fed_funds], axis=1, join="outer")
    df_merged = pd.merge(df_rate, df_fed_funds, on="observation_date", how="inner")

    df_recessions = pd.DataFrame({
        "Date": pd.to_datetime(RECESSIONS)
    })
    df_recessions["Event"] = "Recession Start"

    df_sp_500_peaks = pd.DataFrame({
        "Date": pd.to_datetime(SP_500_PEAKS)
    })
    df_sp_500_peaks["Event"] = "S&P 500 Peak"
    
    # 2. Build an Altair line chart
    line_chart = (
        alt.Chart(df_merged)
        .mark_line()
        .encode(
            #x=alt.X("observation_date:T", scale=alt.Scale(domain=[start_date, df_alt['observation_date'].max()]), title="Date"),
            x=alt.X("observation_date:T", title="Date"),
            # y=alt.Y("lowest_rate_duration:Q", title="Maturity Duration"),
            # tooltip=["observation_date:T", "lowest_rate_duration:Q"]
        )
        .properties(
            width=700,
            height=600,
            title="Lowest Yielding Maturity Time Series"
        )
        .interactive()
    )

    # TODO: fix tooltip 
    lowest_yield_line = line_chart.mark_line(strokeWidth=1).encode(
        y=alt.Y("lowest_rate_duration:Q", title="Maturity Duration"),
        tooltip=[alt.Tooltip("observation_date:T", title="Lowest Yielding Maturity")]
    )

    fed_funds_line = line_chart.mark_line(color="green").encode(
        y=alt.Y("FF:Q", title="Fed Funds Rate"),
        tooltip=[alt.Tooltip("observation_date:T", title="Fed Funds")]
    )

    # --- 4) Create the vertical line chart using mark_rule() ---
    recesssion_start_lines = (
        alt.Chart(df_recessions)
        .mark_rule(color="red", strokeWidth=2)
        .encode(
            x="Date:T",
            color=alt.Color(
                "Event:N",
                legend=alt.Legend(title="Events", orient='bottom'),  
                # scale ensures the legend color matches the lines
                scale=alt.Scale(domain=["Recession Starts", "S&P 500 Peaks"], range=["red", "greenyellow"])
            ),
            tooltip=[alt.Tooltip("Date:T", title="Recession")]  # optional tooltip
        )
    )

    sp_500_peak_lines = (
        alt.Chart(df_sp_500_peaks)
        .mark_rule(color="greenyellow", strokeWidth=1)
        .encode(
            x="Date:T",
            tooltip=[alt.Tooltip("Date:T", title="S&P 500 Peak")]  # optional tooltip
        )
    )


    # --- 5) Layer the vertical lines on top of the main chart ---
    layered_chart = alt.layer(
        #line_chart,
        lowest_yield_line,
        fed_funds_line,
        recesssion_start_lines,
        sp_500_peak_lines
    ).resolve_scale(y="shared").interactive()  # enable zoom and pan if desired

    # --- 6) Display the chart in Streamlit ---
    st.altair_chart(layered_chart, use_container_width=True)

    # *** NEW ***

    print("------------")
    print(df_merged.info())
    print(df_merged.tail())

    df_long = pd.melt(
        df_merged,
        id_vars=["observation_date"],        # Columns to keep
        value_vars=["lowest_rate_duration", "FF"],  # Columns to melt
        var_name="RateType",
        value_name="RateValue"
    )

    print(df_long.info())
    print(df_long.tail())
    print("------------")

 
def lowest_yielding_duration_time_series_chart(sample_rate="W", start_date="1965-01-01"):
    #TODO: add lowest interest rate
    lowest_yield_data = lowest_yield_dataframe(sample_rate=sample_rate)

    # Convert to Altair-friendly format
    #df_rate = lowest_yield_data.reset_index(drop=True)
    df_rate = lowest_yield_data.reset_index()

    df_rate = df_rate[df_rate["observation_date"] >= start_date]

    df_fed_funds = fed_funds_rate_dataframe(start_date=start_date).reset_index()

    # print("RATES COLS", df_rate.columns)
    # print("FF COLS", df_fed_funds.columns)

    df_rate['Category'] = 'Lowest Yielding Maturity'
    df_fed_funds['Category'] = 'Fed Funds Rate'

    # Combine the DataFrames into a single DataFrame 
    #df_alt = pd.concat([df_rate, df_fed_funds], axis=1, join="outer")
    df_merged = pd.merge(df_rate, df_fed_funds, on="observation_date", how="inner")

    lines = (
        alt.Chart(df_merged)
        .transform_fold(
            ["lowest_rate_duration", "FF"],  # original column names
            as_=["variable", "value"]
        )
        .mark_line()
        .encode(
            x="observation_date:T",
            y="value:Q",
            color=alt.Color(
                "variable:N",
                # legend=alt.Legend(
                #     title="Line Type",
                #     orient="bottom",
                #     # Map the original column names to pretty labels
                #     labelExpr="""
                #     {
                #         'lowest_rate_duration': 'Lowest Rate Duration',
                #         'FF': 'Fed Funds Rate',
                #         'Recession Start': 'Recession Start',
                #         'S&P 500 Peak': 'S&P 500 Peak'
                #     }[datum.value] || datum.value
                #     """
                # )
            )
        )
        .properties(
            width=700,
            height=600,
            title="Lowest Yielding Maturity Time Series (FF, 1mo, 3mo, 6mo, 1yr, 2yr, 3yr, 5yr, 7yr, 10yr, 20yr, 30yr)",
        )
    )

    df_recessions = pd.DataFrame({
        "Date": pd.to_datetime(RECESSIONS)
    })
    df_recessions["variable"] = "Recession Start"

    df_sp_500_peaks = pd.DataFrame({
        "Date": pd.to_datetime(SP_500_PEAKS)
    })
    df_sp_500_peaks["variable"] = "S&P 500 Peak"

    df_events = pd.concat([df_recessions, df_sp_500_peaks], ignore_index=True)

    # -----------------------------------------------------------------
    # 4) CREATE THE VERTICAL LINES WITH A SHARED 'variable' FIELD
    # -----------------------------------------------------------------
    rules = (
        alt.Chart(df_events)
        .mark_rule(strokeWidth=1)
        .encode(
            x="Date:T",
            color=alt.Color(
                "variable:N",
                # We'll unify color domain/range with the lines in step 5
                legend=alt.Legend(title="Legend"),
            ),
            tooltip=[
                alt.Tooltip("Date:T", title="Event Date"),
                alt.Tooltip("variable:N", title="Event"),
            ],
        )
    )

    # -----------------------------------------------------------------
    # 5) UNIFY THE COLOR SCALE (LINES + EVENTS) IN ONE LEGEND
    # -----------------------------------------------------------------
    # We have 4 possible categories in 'variable':
    #   1) "lowest_rate_duration"
    #   2) "FF"
    #   3) "Recession Start"
    #   4) "S&P 500 Peak"
    # 
    # We can specify a single domain & range across both layered charts to unify them.
    color_domain = [
        "lowest_rate_duration",
        "FF",
        "Recession Start",
        "S&P 500 Peak"
    ]
    color_range = [
        "#1f77b4",  # blue
        "#2ca02c",  # green
        "red",
        "greenyellow",
    ]

    # Define a shared color scale
    shared_color_scale = alt.Scale(
        domain=color_domain,
        range=color_range
    )

    # Apply that scale to both layer encodings by setting scale=shared_color_scale

    lines = lines.encode(
        color=alt.Color(
            "variable:N",
            scale=shared_color_scale,
            legend=alt.Legend(
                title="Line Type",
                orient="bottom",
                labelExpr="""
                {
                    'lowest_rate_duration': 'Lowest Yielding Duration',
                    'FF': 'Fed Funds Rate',
                    'Recession Start': 'Recession Starts',
                    'S&P 500 Peak': 'S&P 500 Peaks'
                }[datum.value] || datum.value
                """
            )
        )
    )

    rules = rules.encode(
        color=alt.Color(
            "variable:N",
            scale=shared_color_scale,
            legend=alt.Legend(
                title="Line Type",
                orient="bottom"
            )
        )
    )

    final_chart = alt.layer(lines, rules).resolve_scale(color="shared")
    st.altair_chart(final_chart.interactive(), use_container_width=True)


def highest_yielding_duration_time_series_chart(sample_rate="ME", start_date="1965-01-01"):
    #TODO: add in fed funds rate
    #TODO: add highest interest rate
    highest_yield_data = highest_yield_dataframe(sample_rate=sample_rate)

    df_alt = highest_yield_data.reset_index()

    df_alt = df_alt[df_alt["observation_date"] >= start_date]

    df_recessions = pd.DataFrame({
        "Date": pd.to_datetime(RECESSIONS)
    })
    df_recessions["Event"] = "Recession Starts"

    df_recession_ends = pd.DataFrame({
        "Date": pd.to_datetime(RECESSION_ENDS)
    })
    df_recession_ends["Event"] = "Recession Ends"

    # 2. Build an Altair line chart
    line_chart = (
        alt.Chart(df_alt)
        .mark_line()
        .encode(
            x=alt.X("observation_date:T", title="Date"),
            y=alt.Y("highest_rate_duration:Q", title="Maturity Duration"),
            tooltip=["observation_date:T", "highest_rate_duration:Q"]
        )
        .properties(
            width=700,
            height=600,
            title="Highest Yielding Maturity Time Series"
        )
        .interactive()
    )

    # --- 4) Create the vertical line chart using mark_rule() ---
    recession_start_lines = (
        alt.Chart(df_recessions)
        .mark_rule(color="red", strokeWidth=2)
        .encode(
            x="Date:T",
            color=alt.Color(
                "Event:N",
                legend=alt.Legend(title="Events", orient='bottom'),  
                # scale ensures the legend color matches the lines
                scale=alt.Scale(domain=["Recession Starts", "Recession Ends"], range=["red", "blue"])
            ),
            tooltip=[alt.Tooltip("Date:T", title="Event Date")]  # optional tooltip
        )
    )

    recession_end_lines = (
        alt.Chart(df_recession_ends)
        .mark_rule(color="blue", strokeWidth=2)
        .encode(
            x="Date:T",
            tooltip=[alt.Tooltip("Date:T", title="Event Date")]  # optional tooltip
        )
    )

    # --- 5) Layer the vertical lines on top of the main chart ---
    layered_chart = alt.layer(
        line_chart,
        recession_start_lines,
        recession_end_lines
    ).interactive()  # enable zoom and pan if desired

    # --- 6) Display the chart in Streamlit ---
    st.altair_chart(layered_chart, use_container_width=True)


def yield_spread_chart(d1="10-year", d2="2-year"):
    df_yield_spread = create_yield_differential_dataframe(d1, d2)
    df_yield_spread = df_yield_spread.reset_index()

    df_recessions = pd.DataFrame({
        "Date": pd.to_datetime(RECESSIONS[:-2])
    })
    df_recessions["Event"] = "Recession Starts"

    line_chart = (
        alt.Chart(df_yield_spread)
        .mark_line()
        .encode(
            #x=alt.X("observation_date:T", scale=alt.Scale(domain=[start_date, df_alt['observation_date'].max()]), title="Date"),
            x=alt.X("observation_date:T", title="Date"),
            y=alt.Y("Spread:Q", title="Spread"),
            # tooltip=["observation_date:T", "lowest_rate_duration:Q"]
        )
        .properties(
            width=700,
            height=600,
            title=f"Yield Differential: {d1} - {d2}"
        )
        .interactive()
    )

    horizontal_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='gray').encode(
        y='y:Q'
    )

    recesssion_start_lines = (
        alt.Chart(df_recessions)
        .mark_rule(color="red", strokeWidth=2)
        .encode(
            x="Date:T",
            color=alt.Color(
                "Event:N",
                legend=alt.Legend(title="Events", orient='bottom'),  
                # scale ensures the legend color matches the lines
                scale=alt.Scale(domain=["Recession Starts"], range=["red"])
            ),
            tooltip=[alt.Tooltip("Date:T", title="Recession")]  # optional tooltip
        )
    )

    layered_chart = alt.layer(
        line_chart,
        recesssion_start_lines,
        horizontal_line
    ).resolve_scale(y="shared").interactive()  # enable zoom and pan if desired

    # --- 6) Display the chart in Streamlit ---
    st.altair_chart(layered_chart, use_container_width=True)


def readme_section():
    readme_msg = ("The Yield Cuve for U.S. Treasuries has one of the best track records in predicting recessions.\n"
                  "*number predicted since 1950"
                  "*10 - 2 most used"
                  "*problems with 10 - 2, timing"
                  "*September uninversion"
                  "*Chart shows a better visualization of the yield curve, not isolating only a single spread"
                  "abc")
    msg_temp = ("While the 10-year vs. 2-year U.S Treasury spread has had one of the best track records in predicting recessions "
                "since the 1950's, a time series plotting the lowest yielding maturity gives a better insight on the overall "
                "yield curve trend, potentially providing more precise outlooks on recession forecast/timing.........TBD")
    with st.expander("README", expanded=False):
        st.write(msg_temp)
        #st.image("https://placekitten.com/200/300", caption="Cute Cat")


def main():
    st.title("Yield Curve Charts Demo")

    footer = """
     <style>
     .footer {
     position: fixed;
     left: 0;
     bottom: 0;
     width: 100%;
     background-color: #111;
     color: white;
     text-align: center;
     }
     </style>
     <div class="footer">
     <p>By Cade Hutcheson</p>
     </div>
     """
    st.markdown(footer, unsafe_allow_html=True)

    st.divider()

    #maturity_yield_time_series_chart()
    readme_section()
    st.divider()

    yield_spread_chart()
    #yield_spread_chart(d1="30-year", d2="10-year")

    st.divider()

    lowest_yielding_duration_time_series_chart()

    #st.divider()
    #lowest_yielding_duration_time_series_chart(sample_rate="MS")

    st.divider()

    highest_yielding_duration_time_series_chart()


if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.stored_data = {}
    st.session_state.displayed_data = {}
    #st.session_state.maturies = []
    st.session_state.maturities = ["1", "2", "10", "20", "30"]

    st.session_state.selected_maturities = {}
    for mt in st.session_state.maturities:
        st.session_state.selected_maturities[mt] = False


if __name__ == "__main__":
    main()
