import streamlit as st
import pandas as pd
import numpy as np

from utils import create_dataframes
DATA_CSV = "data.csv"


def main():
    st.title("10-Year Stock Price Demo")


    print(st.session_state.selected_maturities)
    # # Sidebar for frequency selection
    # freq = st.sidebar.selectbox(
    #     "Select Frequency",
    #     ["Daily", "Weekly"],
    #     index=0
    # )

    # --- Create a placeholder for the chart at the top ---
    chart_placeholder = st.empty()

    st.markdown("### Customize the Chart Below")

    # Frequency selection
    freq = st.selectbox("Frequency", ["Daily", "Weekly"])

    # Toggle (checkbox) for each stock's visibility
    show_stock_a = st.checkbox("Show Stock A", value=True)
    show_stock_b = st.checkbox("Show Stock B", value=True)
    show_stock_c = st.checkbox("Show Stock C", value=True)

    for mt in st.session_state.maturities:
        st.session_state.selected_maturities[mt] = st.checkbox(mt, value=False)

    # --- Generate 10 years of daily sample data ---
    dates = pd.date_range(start="2014-01-01", periods=3650, freq="D")
    
    # Fake “stock prices” with random walk
    data = {
        "Stock_A": 100 + np.random.normal(0, 1, len(dates)).cumsum(),
        "Stock_B":  50 + np.random.normal(0, 1, len(dates)).cumsum(),
        "Stock_C": 200 + np.random.normal(0, 1, len(dates)).cumsum(),
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"

    # --- Resample if 'Weekly' is selected ---
    if freq == "Weekly":
        df = df.resample("W").mean()  # you could also use .last(), .first(), etc.

    # --- Determine which stocks to show ---
    columns_to_show = []
    if show_stock_a:
        columns_to_show.append("Stock_A")
    if show_stock_b:
        columns_to_show.append("Stock_B")
    if show_stock_c:
        columns_to_show.append("Stock_C")
    if st.session_state.selected_maturities["1"]:
        print("1 SELECTED")

    # --- Render the chart ---
    if columns_to_show:
        # Show selected columns in the chart
        chart_placeholder.line_chart(df[columns_to_show])
    else:
        chart_placeholder.warning("No stocks selected. Please select at least one to display.")

    # Replace "filename.csv" with the actual path to your CSV file
    df_2yr = pd.read_csv(
        "/Users/cadeh/Desktop/MyCode/Workspace/chart_app/data/treasury-constant-maturity/daily_2yr_1976.csv",
        parse_dates=["observation_date"],  # Automatically parse the date column
        index_col="observation_date",      # Set the date column as the DataFrame index
        na_values=[""]                     # Treat blank cells as NaN
    )
    df_10yr = pd.read_csv(
        "/Users/cadeh/Desktop/MyCode/Workspace/chart_app/data/treasury-constant-maturity/daily_10yr_1962.csv",
        parse_dates=["observation_date"],  # Automatically parse the date column
        index_col="observation_date",      # Set the date column as the DataFrame index
        na_values=[""]                     # Treat blank cells as NaN
    )

    print(df_2yr.head())
    df_2yr_filled = df_2yr.fillna(method='ffill')
    df_10yr_filled = df_10yr.fillna(method='ffill')

    df_10yr_filled_weekly = df_10yr_filled.resample("W").mean()
    df_2yr_filled_weekly = df_2yr_filled.resample("W").mean()

    st.line_chart(df_2yr_filled)

    # Join on the date index so both prices align by date
    # 'outer' will include dates that appear in either dataset
    # 'inner' would only include dates common to both
    #df_combined = df_2yr_filled.join(df_10yr_filled, how="outer")
    df_combined_weekly = df_2yr_filled_weekly.join(df_10yr_filled_weekly, how="outer")


    # Show the combined DataFrame (optional)
    # st.write("### Combined Data")
    # st.dataframe(df_combined_weekly.head(10))

    # # Plot both series on one chart
    # st.write("### Chart: 2yr vs 10yr")
    # st.line_chart(df_combined_weekly)

    rate_data = create_dataframes()

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
