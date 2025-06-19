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


if __name__ == "__main__": 
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    file_prefix = 'observation'
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    # get files from monthly directory 
    main_dir = Path('bak')
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # get the previous log data csv
    out_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"

    # extract data from csv
    out_df = pd.read_csv(out_file, usecols=[
        'qc_level', 'stn_id', 'qc1-missing_perc',
        'qc1-expected_obs', 'qc1-actual_obs', 'timestamp',
        'id', 'flagged_error', 'qc2-flagged_var',
        'qc2-flagged_data'
    ])


    # loop through the files
    for file in files:
        df = pd.read_csv(file, index_col=0)
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501

        print(f"Checking validity of data from station id {stn_id[0]}...")

        '''=========================================
        CHANGE RATE CHECKS: Checks the temporal difference or sum of variables
        will raise the `invalid_rate` flag
        '''

        # get the time difference between each observation entry
        # for x in range(len(df)):
        #     df['time_diff'] = (pd.to_datetime(df.index[x]) - pd.to_datetime(df.index[x-1])).total_seconds()


        

        # output a csv
        out_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(out_file, index=False)

        # mark datapoints as within valid range
        df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 2, other=3)
        df.to_csv(file)


        