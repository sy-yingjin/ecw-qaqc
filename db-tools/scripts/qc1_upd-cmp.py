import sys
import os
import glob
import re
import pandas as pd

from pathlib import Path
from calendar import monthrange
import datetime


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
    percentages = dict()

    # indicate the date of log retrieval if there are files to log
    if files:
        today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{today}-log.txt"
        log.parent.mkdir(parents=True, exist_ok=True)

    # open file for logging while checks are run
    with open(log, 'w') as f:

        f.write("===LEVEL 1: OBSERVATION DATA COMPLETENESS CHECK===\n\n")

        # get the num of days of the month
        ndays = monthrange(int(yyyy), int(mm))[1]

        '''
        the rate of observation retrieval per AWS should be 5 mins.

        to determine the completeness of data,
        observation results / (number of 5 minutes per month)

        1 hr has 60mins (12x5)
        1 day has 24hrs (12x24)
        1 month has n-days x 288 five-minutes
        '''
        calc_time = ndays * 288

        # loop through the files
        for file in files:
            stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501
            print(f"Checking observation data of station id {stn_id[0]}...")

            # get data, ensure data types are consistent and updated qc_level
            df = pd.read_csv(file, usecols=[
                'timestamp', 'id', 'pres', 'rr', 'rh', 'temp', 'td', 'wdir',
                'wspd', 'wspdx', 'srad', 'hi', 'station_id', 'wchill',
                # variables that lufft doesn't provide
                'rain', 'tx', 'tn', 'wrun', 'thwi', 'thswi', 'senergy',
                'sradx', 'uvi', 'uvdose', 'uvx', 'hdd', 'cdd', 'et',
                'qc_level', 'wdirx',
            ])
            df['qc_level'] = 1
            df = df.set_index('timestamp')

            # completeness
            observed = df['id'].notna().sum()
            percentages = observed / calc_time * 100
            # gets the missing rows in the .csv
            missing = df['id'].isna().sum() + (calc_time - observed)
            # total 'observed'
            total_obs = len(df)

            f.write(f"STATION ID# {stn_id[0]}\n")
            f.write(f"Percentage of complete data: {round(percentages, 2)}%\n")
            f.write(f"Missing {missing} rows\n")
            f.write(f"Observed Data: {observed} out of {total_obs} rows\n")
            f.write(f"Expected Total Observations: {calc_time}\n\n")

            df.to_csv(file)