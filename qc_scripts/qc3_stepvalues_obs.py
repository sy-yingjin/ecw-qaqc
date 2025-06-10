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

    # loop through files
    for file in files: 
        df = pd.read_csv(file, index_col=0)
        stn_id = re.findall(f"{yyyy}{mm}-(\d+).csv", os.path.basename(file))
        print(f"checking step values for station id {stn_id[0]}...")
        log = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/{file_prefix}-{yyyy}{mm}-{stn_id[0]}-log.txt"
        # open file for logging while checks are run 
        with open(log, 'a') as f: 
            f.write("\n===LEVEL 3: STEP VALUE CHECKS===\nDatapoints with time-based differences outside valid range by station:\n")

            # checking temperature and dew point (diff must not exceed 5C per hour)
            f.write("\nTimestamps where temperature change exceeds 5 degrees Celsius per hour:\n")
            diff_df = df['temp'].diff(periods=6)
            for index, value in diff_df[(diff_df > 5) | (diff_df < -5)].items(): 
                f.write(f" - hourly difference of {round(value,2)}C observed on {index}\n")

            f.write("\nTimestamps where dew point change exceeds 5 degrees Celsius per hour:\n")
            diff_df = df['td'].diff(periods=6) 
            for index, value in diff_df[(diff_df > 5) | (diff_df < -5)].items(): 
                f.write(f" - hourly difference of {round(value,2)}C observed on {index}\n")

            # checking pressure (diff must not exceed 6 mbar per 3 hours)
            f.write("\nTimestamps where pressure change exceeds 6 mbar per three hours:\n")
            diff_df = df['pres'].diff(periods=18) 
            for index, value in diff_df[(diff_df > 6) | (diff_df < -6)].items(): 
                f.write(f" - tri-hourly difference of {round(value,2)} mbar obersved on {index}\n")

            # mark datapoints as within valid range
            df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 2, other=3)

            df.to_csv(file)