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
    percentages_nan = dict() # unused dictionary lol
    # confirmed unused and shocked emily

    # make new index to fit data to, create series for time and day
    # days
    ndays = monthrange(int(yyyy),int(mm))[1]
    idx = pd.date_range(    
        start=pd.to_datetime(f"{mm}/1/{yyyy}"),
        end=pd.to_datetime(f"{mm}/{ndays}/{yyyy} 23:50"), 
        freq='5min', # substitute for period
        tz='Asia/Manila',
    )
    # time
    time = idx.hour
    time = pd.DataFrame(time.rename('time'), index=idx)
    # quirky code bc for some reason there is no DateTimeIndex.day unlike DateTimeIndex.hour 
    # yes there is(?) i don't get how she did time though since it's a different syntax from the documentation
    # https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.hour.html
    day = pd.Series(idx).dt.day
    day = pd.DataFrame({'day':day.values}, index=idx)

    # loop through files 
    for file in files:
        # [] are meant to indicate the things within the set are all they're concerned with
        # \\d means you're finding numerical characters
        # + means there are 2 or more characters to find
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))
        print(f"realigning data for station id {stn_id[0]}...") 
        
        log = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/{file_prefix}-{yyyy}{mm}-{stn_id[0]}-log.txt" 
        log.parent.mkdir(parents=True, exist_ok=True)
        # open file for logging while checks are run
        with open(log, 'w') as f:
            # get data, ensure data types are consistent and update qc_level
            df = pd.read_csv(file, usecols=[
                'timestamp','id','pres','rr','rh','temp','td','wdir','wspd',
                'wspdx','srad','hi','station_id','wchill',
                # variables that lufft doesn't provide
                'rain','tx','tn','wrun','thwi','thswi','senergy',
                'sradx','uvi','uvdose','uvx','hdd','cdd','et','qc_level','wdirx',
            ]) 
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['qc_level'] = 1
            df = df.set_index('timestamp')

            # fit data to new index, add new timestamp column
            # this is filling the gap thrugh neither linear nor block method
            df = df.reindex(index=idx,method='nearest',tolerance='3min')

            # add new column for time and day
            # axis=1 means column
            df = pd.concat([df, time], axis=1, names='hour')
            df = pd.concat([df, day], axis=1, names='day')

            # get percentage na per station for log file 
            # this is a new dictionary ?
            # different from percentage_nan
            percent_nan = df['id'].isna().sum() * 100 / len(df)
            total_nan = df['id'].isna().sum() 

            f.write(f"===LEVEL 1: TIME-SERIES FITTING===\nPercentage of data missing: {round(percent_nan,2)}% missing ({total_nan} rows)\n")

            df.to_csv(file)
