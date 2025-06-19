import sys
import os
import glob
import re
import pandas as pd

from pathlib import Path
from calendar import monthrange


def help_message(nargs):
    if nargs == 0:
        print("missing `year` parameter")
    if nargs < 2:
        print("missing `month` parameter")
    print(f"{sys.argv[0]} yyyy mm")
    sys.exit(2)


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    file_prefix = "observation"
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    # get files from monthly directory
    main_dir = Path("bak")
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # create a new out file to store log data
    out_df = pd.DataFrame(columns=['qc_level','stn_id','qc1-missing_perc','qc1-expected_obs','qc1-actual_obs'])

    '''
    the rate of observation retrieval per AWS should be 5 mins. so to determine the completeness of data,
    observation results / (number of 5 minutes per month)

    1 hr has 60mins (12x5); 1 day has 24hrs (12x24)
    1 month = n-days x 288 five-minutes
    '''
    ndays = monthrange(int(yyyy), int(mm))[1]
    expected_obs = ndays * 288

    # loop through the files
    for file in files:
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501
        print(f"Checking observation data of station id {stn_id[0]}...")

        # get data, ensure data types are consistent and updated qc_level
        df = pd.read_csv(file, usecols=[
            'timestamp', 'id', 'pres', 'rr', 'rh', 'temp', 'td', 'wdir',
            'wspd', 'wspdx', 'srad', 'hi', 'station_id', 'wchill',
            'rain', 'tx', 'tn', 'wrun', 'thwi', 'thswi', 'senergy',
            'sradx', 'uvi', 'uvdose', 'uvx', 'hdd', 'cdd', 'et',
            'qc_level', 'wdirx',
        ])
        df['qc_level'] = 1
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # add new columns for later qc_levels
        df['hour'] = df['timestamp'].dt.hour
        df = df.set_index('timestamp')

        df.to_csv(file)


        # MISSING CHECKING
        # total observations
        actual_obs = len(df)
        # gets the missing rows in the .csv
        missing = expected_obs - actual_obs
        missing_perc = missing / expected_obs * 100

        # store data into the dataframe
        out_df.loc[-1] = [1, stn_id[0], round(missing_perc,2), expected_obs, actual_obs]
        out_df.index += 1
        out_df.sort_index

        # output a csv
        out_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(out_file, index=False)