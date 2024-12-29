import os
import sys

import pandas as pd
import numpy as np

MAIN_DIR = os.path.dirname(os.path.realpath(__file__))
CONSTANT_MATURITIES_DATA_DIR = os.path.join(MAIN_DIR, "data", "treasury-constant-maturity")
FED_FUNDS_CSV_FILE = os.path.join(CONSTANT_MATURITIES_DATA_DIR, "weeklyFF_0mo_1954.csv")

RECESSIONS = ["2020-03-30", "2007-12-01", "2001-03-01", "1990-07-01", "1981-07-01", "1980-01-01", "1973-11-01", "1969-12-01"]
RECESSION_ENDS = ["2020-04-01", "2009-06-01", "2001-11-01", "1991-03-01", "1982-11-01", "1975-03-01", "1970-11-01"]

SP_500_PEAKS = ["2022-01-01", "2020-02-01", "2007-10-01", "2000-03-01", "1987-08-01", "1980-11-01", "1973-01-01", "1968-11-01"]


def load_rate_data_for_maturity(maturity):
    ...


def get_available_maturities(data_directory_path):
    data_files = [file for file in os.listdir(data_directory_path) if file.endswith('.csv')]

    maturities = [parse_duration_from_filename(file) for file in data_files]
    #TODO: make maturity:filename dict

    months = sorted([m for m in maturities if m.endswith('month')])
    years = sorted([m for m in maturities if m.endswith('year')], key=lambda x: int(x.split("-")[0]))

    return months + years


def create_dataframes(data_directory_path=CONSTANT_MATURITIES_DATA_DIR, fillna=True, sample_rate="W"):
    """
    create yield time series dataframes from all csv files in given directory
    """
    data_files = [os.path.join(data_directory_path, file)
                    for file in os.listdir(data_directory_path)
                        if file.endswith('.csv')]

    #data_files = data_files[:3]
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

        # forward fill empty and convert from daily to weekly
        if fillna:
            dataframe = dataframe.fillna(method='ffill')
        dataframe = dataframe.resample(sample_rate).mean()
        #dataframe = dataframe.resample("ME").mean()
        dataframe.title = duration

        maturity_datafile_dict[duration] = dataframe

    return maturity_datafile_dict


def lowest_yield_dataframe(sample_rate="W"):
    yield_dfs = create_dataframes(fillna=False, sample_rate=sample_rate)

    converted_keys_dfs = {}
    for duration, df in yield_dfs.items():
        dur_num = duration.split('-')[0]
        if duration.endswith("month"):
            converted_keys_dfs[round(int(dur_num)/12, 3)] = df
        else:
            converted_keys_dfs[int(dur_num)] = df

    #print(sys.getsizeof(yield_dfs))
    #print(sys.getsizeof(converted_keys_dfs))
    #print(converted_keys_dfs.keys())

    combined_df = pd.concat(converted_keys_dfs, axis=1, join="outer")
    #TODO: columns have 2 different values -> ex: 1.00 and 1-year -> title not being replaced? 
    lowest_yields = combined_df.idxmin(axis=1)

    # 5. Build a new DataFrame with the index=Date and a single column: 'lowest_stock'
    lowest_df = pd.DataFrame({"lowest_yield": lowest_yields})

    lowest_df.columns = ["lowest_rate_duration"]
    # extract the first element from the tuple
    lowest_df["lowest_rate_duration"] = lowest_df["lowest_rate_duration"].apply(lambda x: x[0])

    print(combined_df.head())
    print(lowest_df.head())
    print(lowest_df.tail())
    print(lowest_df.info())
    print(type(lowest_df))
    return lowest_df


def highest_yield_dataframe(sample_rate="ME"):
    yield_dfs = create_dataframes(fillna=False, sample_rate=sample_rate)

    converted_keys_dfs = {}
    for duration, df in yield_dfs.items():
        dur_num = duration.split('-')[0]
        if duration.endswith("month"):
            converted_keys_dfs[round(int(dur_num)/12, 3)] = df
        else:
            converted_keys_dfs[int(dur_num)] = df

    #print(sys.getsizeof(yield_dfs))
    #print(sys.getsizeof(converted_keys_dfs))
    #print(converted_keys_dfs.keys())

    combined_df = pd.concat(converted_keys_dfs, axis=1, join="outer")
    #TODO: columns have 2 different values -> ex: 1.00 and 1-year -> title not being replaced? 
    highest_yields = combined_df.idxmax(axis=1)

    # 5. Build a new DataFrame with the index=Date and a single column: 'highest_stock'
    highest_df = pd.DataFrame({"highest_yield": highest_yields})

    highest_df.columns = ["highest_rate_duration"]
    # extract the first element from the tuple
    highest_df["highest_rate_duration"] = highest_df["highest_rate_duration"].apply(lambda x: x[0])

    # print(combined_df.head())
    # print(highest_df.head())
    # print(highest_df.tail())
    # print(highest_df.info())
    # print(type(highest_df))
    return highest_df


def convert_samples_to_weekly(df):
    return df.resample("W").mean()  # you could also use .last(), .first(), etc.


def parse_duration_from_filename(csv_filepath):
    filename = os.path.basename(csv_filepath)
    duration_abrev = filename.split("_")[1]

    if duration_abrev.endswith('yr'):
        years = duration_abrev.split('yr')[0]
        return f"{years}-year"
    elif duration_abrev.endswith('mo'):
        months = duration_abrev.split('mo')[0]
        return f"{months}-month"
    else:
        print("invalid name")
        return None


def fed_funds_rate_dataframe(start_date="1965-01-01"):
    duration = "FF"
    dataframe = pd.read_csv(
        FED_FUNDS_CSV_FILE,
        parse_dates=["observation_date"],  # Automatically parse the date column
        index_col="observation_date",      # Set the date column as the DataFrame index
        na_values=[""]                     # Treat blank cells as NaN
    )

    second_column_name = dataframe.columns[0]  # Get the current name of the second column
    dataframe.rename(columns={second_column_name: duration}, inplace=True)

    # forward fill empty and convert from daily to weekly
    #if fillna:
    dataframe = dataframe.fillna(method='ffill')
    #dataframe = dataframe.resample(sample_rate).mean()
    dataframe = dataframe.resample("W").mean()
    dataframe.title = duration

    #dataframe = dataframe[dataframe["observation_date"] >= start_date]
    print(dataframe.head())
    print(dataframe.tail())
    print(dataframe.info())
    return dataframe


def create_yield_differential_dataframe(d1, d2):
    df_yields_dict = create_dataframes()
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

    print(df_spread.tail())
    print(df_spread.head())
    print(df_spread.info())

    return df_spread


if __name__ == "__main__":
    # res = get_available_maturities(CONSTANT_MATURITIES_DATA_DIR)
    # print(res)

    #highest_yield_dataframe()

    create_yield_differential_dataframe("10-year", "2-year")