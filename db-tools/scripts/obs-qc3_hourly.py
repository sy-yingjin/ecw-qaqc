import sys
import os
import glob
import re

import pandas as pd

from pathlib import Path


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


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    file_prefix = "observation"
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    # get files from monthly directory
    main_dir = Path('bak')
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # get the previous log data csv
    check_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"


    # loop through the files
    for file in files:
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501
        stn_type = get_stn_type(int(stn_id[0]))

        print(f"Converting {stn_id[0]} data to hourly reports...")

        if stn_type=='MO':
            # The observation data is from a Davis AWS
            col_names = [
                'timestamp',
                'pres', 'rr', 'rh', 'temp', 'td', 'wdir',
                'wspd', 'wspdx', 'srad', 'hi', 'wchill',
                'rain', 'tx', 'tn', 'wrun', 'thwi', 'thswi',
                'senergy','sradx', 'uvi', 'uvdose',
                'uvx', 'hdd', 'cdd', 'et', 'wdirx',
            ]
        elif stn_type=='SMS':
            # The observation data is from a Lufft AWS
            col_names = [
                'timestamp',
                'pres','rr','rh','temp','td','wdir','wspd',
                'wspdx','srad','mslp','hi','wchill',
            ]

        df = pd.read_csv(file, usecols=col_names)
        df = df[col_names]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort the main observation dataframe to an hourly state
        # all observations will be averaged
        hourly_df = df.groupby(pd.Grouper(key='timestamp',freq='h'))[col_names[1:]].mean().round(2)
        hourly_df.insert(0, 'qc_level', 3)


        # output a csv
        hourly_df.to_csv(file)