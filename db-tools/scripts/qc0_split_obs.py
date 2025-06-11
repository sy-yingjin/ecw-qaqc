import sys
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

    # directory to get the files from, can be changed depending on where files are
    file_dir = Path('bak')
    file = file_dir / f"{yyyy}/{file_prefix}-{yyyy}{mm}.csv"

    # extract data from csv, ignoring date_created and date_updated
    # modfied the columns to be able to 
    df = pd.read_csv(file, usecols=[
        'timestamp','id','pres','rr','rh','temp','td','wdir','wspd',
        'wspdx','srad','hi','station_id','wchill','rain','tx','tn','wrun','thwi','thswi','senergy','sradx','uvi','uvdose','uvx','hdd','cdd','et','qc_level','wdirx',

    ]) 

    # get list of unique ids to sort data by station id 
    uniq_ids = df.station_id.unique()
    df_dict = {stn : pd.DataFrame() for stn in uniq_ids}

    for key in df_dict.keys():
        # sort each station data by timestamp for easier manipulation later
        df_dict[key] = df[:][df.station_id == key]
        df_dict[key] = df_dict[key].sort_values(by='timestamp')

        # create new monthly and station directory in folder
        out_file = file_dir / f"{yyyy}/{mm}/{file_prefix}-{yyyy}{mm}-{key}.csv"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        df_dict[key].to_csv(out_file, index=False)