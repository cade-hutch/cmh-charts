from datetime import date
import os

from fredapi import Fred
import pandas as pd

MAIN_DIR = os.path.dirname(os.path.realpath(__file__))
CONSTANT_MATURITIES_DATA_DIR = os.path.join(MAIN_DIR, "data", "treasury-constant-maturity")
FED_FUNDS_CSV_FILE = os.path.join(CONSTANT_MATURITIES_DATA_DIR, "FF.csv")

TREASURY_SERIES = ["FF", "DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"]

RECESSIONS = ["2020-03-30", "2007-12-01", "2001-03-01", "1990-07-01", "1981-07-01", "1980-01-01", "1973-11-01", "1969-12-01"]
RECESSION_ENDS = ["2020-04-30", "2009-06-01", "2001-11-01", "1991-03-01", "1982-11-01", "1975-03-01", "1970-11-01"]

SP_500_PEAKS = ["2022-01-01", "2020-02-01", "2007-10-01", "2000-03-01", "1987-08-01", "1980-11-01", "1973-01-01", "1968-11-01"]
SP_500_TROUGHS = ["2022-10-01", "2020-03-01", "2009-03-01", "2002-10-01", "1987-12-01", "1982-08-01", "1974-10-01", "1970-05-01"]


def update_csv_files(day_until_stale=7):
    """
    Download fresh yield data if stored data is older than the given amount of days

    CSV dates in "YYYY-MM-DD" format
    """
    current_date = date.today()

    yield_data_file = os.path.join(CONSTANT_MATURITIES_DATA_DIR, TREASURY_SERIES[-1] + ".csv")
    if not os.path.exists(yield_data_file):
        download_fred_data()
        return

    df = pd.read_csv(yield_data_file)

    last_date = pd.to_datetime(df['observation_date'].iloc[-1]).date()

    print(f"Yield data is {(current_date - last_date).days} days old")
    if (current_date - last_date).days >= day_until_stale:
        print('downloading data')
        download_fred_data()
    else:
        print("data is fresh")


def download_fred_data():
    """
    Use FRED API to download treasury time series data and save to csvs
    """
    if "FRED_API_KEY" not in os.environ:
        return
    
    fred = Fred(api_key=os.environ["FRED_API_KEY"])

    for duration in TREASURY_SERIES:
        data = fred.get_series(duration)

        data.name = duration

        csv_filename = os.path.join(CONSTANT_MATURITIES_DATA_DIR, duration + ".csv")

        data.to_csv(csv_filename, index_label="observation_date") 


def create_yield_df_dict(data_directory_path=CONSTANT_MATURITIES_DATA_DIR, fillna=True, sample_rate="W"):
    """
    Create yield time series dataframes from all csv files in given directory

    Returns:
        dict(str : DataFrame)
    """
    data_files = [os.path.join(data_directory_path, file)
                    for file in os.listdir(data_directory_path)
                        if file.endswith('.csv')]

    maturity_datafile_dict = {}

    for file in data_files:
        duration = parse_duration_from_filename(file)
        dataframe = pd.read_csv(
            file,
            parse_dates=["observation_date"],  # Automatically parse the date column
            index_col="observation_date",      # Set the date column as the DataFrame index
            na_values=[""]                     # Treat blank cells as NaN
        )

        second_column_name = dataframe.columns[0]  # Get the current name of the second column
        dataframe.rename(columns={second_column_name: duration}, inplace=True)

        # forward fill any empty rows and convert to sample rate
        if fillna:
            dataframe = dataframe.ffill()
        dataframe = dataframe.resample(sample_rate).mean()
        dataframe.title = duration

        maturity_datafile_dict[duration] = dataframe

    return maturity_datafile_dict


def create_yield_dataframe():
    """
    Create dataframe that concats all yield dataframes together
    Create columns for highest/lowest yields and min max spread
    """
    yields_df_dict = create_yield_df_dict(fillna=False)

    combined_df = pd.concat(list(yields_df_dict.values()), axis=1, join="outer")

    combined_df["Highest Yield"] = combined_df.max(axis=1)
    combined_df["Lowest Yield"] = combined_df.min(axis=1)

    combined_df["Min Max Spread"] = combined_df["Highest Yield"] - combined_df["Lowest Yield"]

    return combined_df


def lowest_yield_dataframe(sample_rate="W"):
    """
    Create time indexed dataframe with column for weekly lowest yield treasury duration.
    Represent durations as float conversion of years('1-year' -> 1.0, '6-month' -> 0.5)
    """
    yield_dfs = create_yield_df_dict(fillna=False, sample_rate=sample_rate)

    converted_keys_dfs = {}
    for duration, df in yield_dfs.items():
        dur_num = duration.split('-')[0]
        if duration.endswith("month"):
            converted_keys_dfs[round(int(dur_num)/12, 3)] = df
        else:
            converted_keys_dfs[int(dur_num)] = df

    combined_df = pd.concat(converted_keys_dfs, axis=1, join="outer")
    lowest_yields = combined_df.idxmin(axis=1)

    lowest_df = pd.DataFrame({"lowest_rate_duration": lowest_yields})

    # extract the first element from the (duration float, duration string) tuple
    lowest_df["lowest_rate_duration"] = lowest_df["lowest_rate_duration"].apply(lambda x: x[0])

    return lowest_df


def highest_yield_dataframe(sample_rate="ME"):
    """
    Create time indexed dataframe with column for monthly highest yield treasury duration.
    Represent durations as float conversion of years('1-year' -> 1.0, '6-month' -> 0.5)
    """
    yield_dfs = create_yield_df_dict(fillna=False, sample_rate=sample_rate)

    converted_keys_dfs = {}
    for duration, df in yield_dfs.items():
        dur_num = duration.split('-')[0]
        if duration.endswith("month"):
            converted_keys_dfs[round(int(dur_num)/12, 3)] = df
        else:
            converted_keys_dfs[int(dur_num)] = df

    combined_df = pd.concat(converted_keys_dfs, axis=1, join="outer")
    highest_yields = combined_df.idxmax(axis=1)

    highest_df = pd.DataFrame({"highest_rate_duration": highest_yields})

    # extract the first element from the (duration float, duration string) tuple
    highest_df["highest_rate_duration"] = highest_df["highest_rate_duration"].apply(lambda x: x[0])

    return highest_df


def parse_duration_from_filename(csv_filepath):
    """
    Convert duration titles to more readable format('DGS1' -> '1-year', 'DGS3MO' -> '3-month')
    """
    filename = os.path.basename(csv_filepath).split(".")[0]

    if filename.startswith("FF"):
        return "0-month"

    duration_abrev = filename.split("DGS")[1]

    if duration_abrev.endswith('MO'):
        months = duration_abrev.split('MO')[0]
        return f"{months}-month"
    else:
        return f"{duration_abrev}-year"


def fed_funds_rate_dataframe(start_date="1965-01-01"):
    """
    Create separate dataframe for Fed Funds Rate data
    """
    duration = "FF"
    dataframe = pd.read_csv(
        FED_FUNDS_CSV_FILE,
        parse_dates=["observation_date"],
        index_col="observation_date",
        na_values=[""]
    )

    dataframe = dataframe.ffill()
    dataframe = dataframe.resample("W").mean()
    dataframe.title = duration

    return dataframe


def create_yield_differential_dataframe(d1, d2):
    """
    Create dataframe for a treasury yield spread (ex: 10 year - 2 year)
    """
    df_yields_dict = create_yield_df_dict()
    if d1 not in df_yields_dict or d2 not in df_yields_dict:
        print("invalid durations input")
        return None
    
    df1 = df_yields_dict[d1]
    df2 = df_yields_dict[d2]

    second_column_name = df1.columns[0]
    df1.rename(columns={second_column_name: "yield"}, inplace=True)
    second_column_name = df2.columns[0]
    df2.rename(columns={second_column_name: "yield"}, inplace=True)
    
    d1_float = 0
    d2_float = 0

    if d1.endswith("month"):
            d1_float = round(int(d1.split("mo")[0])/12, 3)
    else:
        d1_float = float(d1.split("-")[0])
    
    if d2.endswith("month"):
        d2_float = round(int(d2.split("-")[0])/12, 3)
    else:
        d2_float = float(d2.split("-")[0])

    if d2_float > d1_float:
        df1, df2 = df1, df2

    df_spread = pd.DataFrame({
        "Spread": (df1["yield"] - df2["yield"]).dropna()
    })

    return df_spread


if __name__ == "__main__":
    ...
    #update_csv_files()