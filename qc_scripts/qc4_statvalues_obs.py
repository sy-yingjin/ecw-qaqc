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
    file_prefix = 'observation'
    yyyy = sys.argv[1]
    mm = sys.argv[2] 

    # get files from monthly directory 
    main_dir = Path('bak')
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # make new index to fit data to, create series for time and day
    ndays = monthrange(int(yyyy),int(mm))[1]
    idx = pd.date_range(    
        start=pd.to_datetime(f"{mm}/1/{yyyy}"),
        end=pd.to_datetime(f"{mm}/{ndays}/{yyyy} 23:50"), 
        freq='10min',
        tz='Asia/Manila',
    )

    # loop through files
    for file in files:
        df = pd.read_csv(file, index_col=0)
        stn_id = re.findall(f"{yyyy}{mm}-(\d+).csv", os.path.basename(file))
        print(f"checking variance of values for station id {stn_id[0]}...")
        log = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/{file_prefix}-{yyyy}{mm}-{stn_id[0]}-log.txt"
        # open file for logging while checks are run 
        with open(log, 'a') as f:  
            f.write("\n===LEVEL 4: STATISTICAL CHECKS===\nDatapoints with variances outside valid range by station:\n")

            # checking temperature 
            f.write("Timestamps where standard deviation over 12 hours of temperature / dew point is less than 0.5 degrees Celsius:\n")
            for i in range(len(df)-72): 
                start = i 
                end = i + 72 
                temp_sd = df['temp'].iloc[start:end].std(skipna=True)
                td_sd = df['td'].iloc[start:end].std(skipna=True)
                if temp_sd < 0.5: f.write(f" - observed temperature sd of {temp_sd} C on {idx[i]}\n")
                if td_sd < 0.5: f.write(f" - observed dew point sd of {td_sd} C on {idx[i]}\n")
                i += 1

            # checking wind direction 
            f.write("Timestamps where standard deviation over 18 hours of wind direction is less than 10 degrees:\n")
            for i in range(len(df)-108): 
                start = i 
                end = i + 108 
                wdr_sd = df['wdir'].iloc[start:end].std(skipna=True)
                if wdr_sd < 10: f.write(f" - observed wind direction sd of {wdr_sd} degrees on {idx[i]}\n")
                i += 1

            # checking wind speed 
            f.write("Timestamps where standard deviation over 3 hours of wind speed is less than 0.36 km/hr:\n")
            for i in range(len(df)-18): 
                start = i 
                end = i + 18 
                wspd_sd = df['wspd'].iloc[start:end].std(skipna=True)
                if wspd_sd < 0.36: f.write(f" - observed wind speed sd of {wspd_sd} km/hr on {idx[i]}\n")
                i += 1

            # mark datapoints as within valid range
            df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 3, other=4)

            in_folder = main_dir / f"{yyyy}/{mm}/{file_prefix}-{yyyy}{mm}.csv"
            df.to_csv(file)