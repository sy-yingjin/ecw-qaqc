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
    percentages_nan = dict()

    # make new index to fit data to, create series for time and day
    ndays = monthrange(int(yyyy),int(mm))[1]
    idx = pd.date_range(    
        start=pd.to_datetime(f"{mm}/1/{yyyy}"),
        end=pd.to_datetime(f"{mm}/{ndays}/{yyyy} 23:50"), 
        freq='10min',
        tz='Asia/Manila',
    )
    time = idx.hour
    time = pd.DataFrame(time.rename('time'), index=idx)
    # quirky code bc for some reason there is no DateTimeIndex.day unlike DateTimeIndex.hour 
    day = pd.Series(idx).dt.day
    day = pd.DataFrame({'day':day.values}, index=idx)

    # loop through files 
    for file in files:
        stn_id = re.findall(f"{yyyy}{mm}-(\d+).csv", os.path.basename(file))
        print(f"realigning data for station id {stn_id[0]}...") 
        
        log = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/{file_prefix}-{yyyy}{mm}-{stn_id[0]}-log.txt" 
        log.parent.mkdir(parents=True, exist_ok=True)
        # open file for logging while checks are run
        with open(log, 'w') as f:
            # get data, ensure data types are consistent and update qc_level
            df = pd.read_csv(file,usecols=[
                'id','pres','rr','rh','temp','td','wdir','wspd',
                'wspdx','srad','mslp','hi','wchill','qc_level','timestamp',
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['qc_level'] = 1
            df = df.set_index('timestamp')

            # fit data to new index, add new timestamp column
            df = df.reindex(index=idx,method='nearest',tolerance='3min')

            # add new column for time and day
            df = pd.concat([df, time], axis=1, names='hour')
            df = pd.concat([df, day], axis=1, names='day')

            # get percentage na per station for log file 
            percent_nan = df['id'].isna().sum() * 100 / len(df)
            total_nan = df['id'].isna().sum() 

            f.write(f"===LEVEL 1: TIME-SERIES FITTING===\nPercentage of data missing: {round(percent_nan,2)}% missing ({total_nan} rows)\n")

            df.to_csv(file)
