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

def get_stn_type(id):
    stn_dir = Path('bak')
    stn_file = stn_dir / "stn/stn-type.csv"

    # extract data from stn csv
    stn_df = pd.read_csv(stn_file, usecols=[
        'id', 'station_type'
    ])
    aws = stn_df.loc[(stn_df['id'] == (id)),'station_type'].item()
    return aws


def qc1_missing(yyyy,mm):
    file_prefix = "observation"

    # get files from monthly directory
    main_dir = Path('bak')
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # create a csv to store quality check data
    check_df = pd.DataFrame(columns=['qc_level','stn_id','qc1-missing_perc','qc1-expected_obs','qc1-actual_obs'])

    # get the number of days in the month
    ndays = monthrange(int(yyyy), int(mm))[1]


    # loop through files
    for file in files:
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file)) # noqa: E501

        print(f"Checking observation data of station id {stn_id[0]}...")
        stn_type = get_stn_type(int(stn_id[0]))

        # get columns excluding station_id, id created_on and updated_on
        if stn_type=='MO':
            # The observation data is from a Davis AWS
            col_names = [
                'timestamp', 'id', 'qc_level',
                'pres', 'rr', 'rh', 'temp', 'td', 'wdir',
                'wspd', 'wspdx', 'srad', 'hi', 'wchill',
                'rain', 'tx', 'tn', 'wrun', 'thwi', 'thswi',
                'senergy','sradx', 'uvi', 'uvdose',
                'uvx', 'hdd', 'cdd', 'et', 'wdirx',
            ]
            freq = 288
        elif stn_type=='SMS':
            # The observation data is from a Lufft AWS
            col_names = [
                'timestamp', 'id', 'qc_level',
                'pres','rr','rh','temp','td','wdir','wspd',
                'wspdx','srad','mslp','hi','wchill',
            ]
            freq = 144
        
        df = pd.read_csv(file, usecols=col_names)
        df = df[col_names]
        df['qc_level'] = 1

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index("timestamp")

        # converts utc -> local time
        df = df.tz_convert("Asia/Manila")
        df.to_csv(file)

        # know the frequency to know the expected observations
        expected_obs = ndays * freq

        # MISSING CHECK
        actual_obs = len(df)
        missing = expected_obs - actual_obs
        missing_perc = missing / expected_obs * 100

        # store check data into the check_df
        check_df.loc[-1] = [1, stn_id[0], round(missing_perc,2), expected_obs, actual_obs]
        check_df.index += 1
        check_df.sort_index

        # output the check_df into a csv file
        check_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"
        check_file.parent.mkdir(parents=True, exist_ok=True)
        check_df.to_csv(check_file, index=False)


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    qc1_missing(yyyy,mm)