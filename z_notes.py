"""
1mo - 2001 X
3mo - 1981 X
6mo - 1981 X
1yr - 1962
2yr - 1976 X
3yr - 1962
5yr - 1962
7yr - 1969
10yr - 1962
20yr - 1962
30yr - 1977
"""
"""
February 2020 - April 2020 (COVID-19 Recession)
December 2007 - June 2009 (Great Recession)
March 2001 - November 2001 (Dot-com Bubble Recession)
July 1990 - March 1991 (Early 1990s Recession)
July 1981 - November 1982 (Early 1980s Recession)
November 1973 - March 1975 (1973-1975 Recession)
December 1969 - November 1970 (1969-1970 Recession)
April 1960 - February 1961 (1960-1961 Recession)
August 1957 - April 1958 (1957-1958 Recession)

10yr-2yr spread on recession start:
1980: -0.43
1981: -0.87
1990: 0.2
2001: 0.47
2007: 1.02
2020: 0.22

inversion spike falling edge -> start of recession:
1980: N/A
1981: N/A
1990: 10 months / 5 months
2001: 1-2 months / -1-2 months / 5-6 months
2007: 6-7 months
2020: 6-7 months

10yr-2yr uninversion -> start of recession:
1980: N/A
1981: N/A
1990: 12 months (2 following reinversions)
2001: 2-3 months
2007: 6-7 months / 18 months
2020: 6-7 months

S&P 500 Peaks-Troughs (since 1968):
November 1968 - May 1970
Jan 73 - Oct 74
Nov 80 - Aug 82
Aug 1987 - Dec 1987
March 2000 - Oct 2002
Oct 2007 - March 2009
Feb 2020 - March 2020
Jan 2022 - Oct 2022

TODO: 
    - X differential between highest and lowest current rates
    - S&P layer
    - 10yr treasury performance from low yield spike to recession start/end
    - X upload streamlit
    - readme section
    - switch to downloading data or updating csvs to stay up to date
    - differnetial chart func optional params for add ins
    - make tool tips better
    - pd.melt()

"""


"""
PANDAS NOTES:

DataFrame:

# ** from dictionary, where keys are column names and values are column data **
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)

# ** from dictionary of dict values, where keys are row names and values are {column:column data} **
data = {
    'row1': {'Name': 'Alice', 'Age': 25},
    'row2': {'Name': 'Bob', 'Age': 30}
}
df = pd.DataFrame.from_dict(data, orient='index')

# ** Pandas series as columns **
data = {
    'Name': pd.Series(['Alice', 'Bob']),
    'Age': pd.Series([25, 30])
}
df = pd.DataFrame(data)

# ** from list of lists, where lists are colum data
data = [
    ['Alice', 25, 'New York'],
    ['Bob', 30, 'Los Angeles']
]
df = pd.DataFrame(data, columns=['Name', 'Age', 'City'])

# ** from list of dictionaries, where each dict element is a row
data = [
    {'Name': 'Alice', 'Age': 25},
    {'Name': 'Bob', 'Age': 30}
]
df = pd.DataFrame(data)
"""


# def lowest_yielding_duration_time_series_chart_OLD(sample_rate="W", start_date="1965-01-01"):
#     #TODO: add lowest interest rate
#     lowest_yield_data = lowest_yield_dataframe(sample_rate=sample_rate)

#     # Convert to Altair-friendly format
#     #df_rate = lowest_yield_data.reset_index(drop=True)
#     df_rate = lowest_yield_data.reset_index()

#     df_rate = df_rate[df_rate["observation_date"] >= start_date]

#     df_fed_funds = fed_funds_rate_dataframe(start_date=start_date).reset_index()

#     # print("RATES COLS", df_rate.columns)
#     # print("FF COLS", df_fed_funds.columns)

#     df_rate['Category'] = 'Lowest Yielding Maturity'
#     df_fed_funds['Category'] = 'Fed Funds Rate'

#     # Combine the DataFrames into a single DataFrame 
#     #df_alt = pd.concat([df_rate, df_fed_funds], axis=1, join="outer")
#     df_merged = pd.merge(df_rate, df_fed_funds, on="observation_date", how="inner")

#     df_recessions = pd.DataFrame({
#         "Date": pd.to_datetime(RECESSIONS)
#     })
#     df_recessions["Event"] = "Recession Start"

#     df_sp_500_peaks = pd.DataFrame({
#         "Date": pd.to_datetime(SP_500_PEAKS)
#     })
#     df_sp_500_peaks["Event"] = "S&P 500 Peak"
    
#     # 2. Build an Altair line chart
#     line_chart = (
#         alt.Chart(df_merged)
#         .mark_line()
#         .encode(
#             #x=alt.X("observation_date:T", scale=alt.Scale(domain=[start_date, df_alt['observation_date'].max()]), title="Date"),
#             x=alt.X("observation_date:T", title="Date"),
#             # y=alt.Y("lowest_rate_duration:Q", title="Maturity Duration"),
#             # tooltip=["observation_date:T", "lowest_rate_duration:Q"]
#         )
#         .properties(
#             width=700,
#             height=600,
#             title="Lowest Yielding Maturity Time Series"
#         )
#         .interactive()
#     )

#     # TODO: fix tooltip 
#     lowest_yield_line = line_chart.mark_line(strokeWidth=1).encode(
#         y=alt.Y("lowest_rate_duration:Q", title="Maturity Duration"),
#         tooltip=[alt.Tooltip("observation_date:T", title="Lowest Yielding Maturity")]
#     )

#     fed_funds_line = line_chart.mark_line(color="green").encode(
#         y=alt.Y("FF:Q", title="Fed Funds Rate"),
#         tooltip=[alt.Tooltip("observation_date:T", title="Fed Funds")]
#     )

#     # --- 4) Create the vertical line chart using mark_rule() ---
#     recesssion_start_lines = (
#         alt.Chart(df_recessions)
#         .mark_rule(color="red", strokeWidth=2)
#         .encode(
#             x="Date:T",
#             color=alt.Color(
#                 "Event:N",
#                 legend=alt.Legend(title="Events", orient='bottom'),  
#                 # scale ensures the legend color matches the lines
#                 scale=alt.Scale(domain=["Recession Starts", "S&P 500 Peaks"], range=["red", "greenyellow"])
#             ),
#             tooltip=[alt.Tooltip("Date:T", title="Recession")]  # optional tooltip
#         )
#     )

#     sp_500_peak_lines = (
#         alt.Chart(df_sp_500_peaks)
#         .mark_rule(color="greenyellow", strokeWidth=1)
#         .encode(
#             x="Date:T",
#             tooltip=[alt.Tooltip("Date:T", title="S&P 500 Peak")]  # optional tooltip
#         )
#     )


#     # --- 5) Layer the vertical lines on top of the main chart ---
#     layered_chart = alt.layer(
#         #line_chart,
#         lowest_yield_line,
#         fed_funds_line,
#         recesssion_start_lines,
#         sp_500_peak_lines
#     ).resolve_scale(y="shared").interactive()  # enable zoom and pan if desired

#     # --- 6) Display the chart in Streamlit ---
#     st.altair_chart(layered_chart, use_container_width=True)

#     # *** NEW ***

#     # print("------------")
#     # print(df_merged.info())
#     # print(df_merged.tail())

#     df_long = pd.melt(
#         df_merged,
#         id_vars=["observation_date"],        # Columns to keep
#         value_vars=["lowest_rate_duration", "FF"],  # Columns to melt
#         var_name="RateType",
#         value_name="RateValue"
#     )

#     # print(df_long.info())
#     # print(df_long.tail())
#     # print("------------")

 