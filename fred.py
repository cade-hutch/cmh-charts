import os
from fredapi import Fred

MAIN_DIR = os.path.dirname(os.path.realpath(__file__))
CONSTANT_MATURITIES_DATA_DIR = os.path.join(MAIN_DIR, "data", "treasury-constant-maturity")

TREASURY_SERIES = ["FF", "DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"]

fred = Fred(api_key='f0744f51c743b28c4c44bce84a7350e8')

# Example: Fetch data for the U.S. 10-Year Treasury Yield (ID: 'DGS10')

for duration in TREASURY_SERIES:
    data = fred.get_series(duration)

    data.name = duration

    csv_filename = os.path.join(CONSTANT_MATURITIES_DATA_DIR, duration + ".csv")

    data.to_csv(csv_filename, index_label="observation_date") 

# Print the data
# print(type(data))
# print(len(data))
# print(data.tail())
metadata = fred.get_series_info('DGS10')

# Print metadata
print(metadata)
