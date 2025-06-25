import sys
import pandas as pd
import pytz

from datetime import datetime
from pathlib import Path
from calendar import monthrange
from helpers.db import get_data, get_stn

tz = pytz.timezone("Asia/Manila")


def help_message(nargs):
    if nargs == 0:
        print("missing `year` parameter")
    if nargs < 2:
        print("missing `month` parameter")
    print(f"{sys.argv[0]} yyyy mm")
    sys.exit(2)

def validate_request(yyyy,mm):
    input_date = pd.to_datetime(datetime.strptime(f"{yyyy}-{mm}-01", "%Y-%m-%d")).tz_localize('Asia/Manila')
    current_date = pd.to_datetime(datetime.now()).tz_localize('Asia/Manila')
    lim_date = pd.to_datetime(datetime.strptime("2010-01-01", "%Y-%m-%d")).tz_localize('Asia/Manila')

    return (input_date < lim_date) or (input_date > current_date)


def qc0_splitstation(yyyy,mm):
    file_suffix = "observation"
    out_dir = Path("bak")

    # get an updated list of stations and their station type
    stn_df = get_stn()

    # create a monthly and station directory in folder
    stn_file = out_dir / "stn-type.csv"
    stn_file.parent.mkdir(parents=True, exist_ok=True)
    stn_df.to_csv(stn_file,index=False)

    # is the requested year and month valid?
    if validate_request(yyyy,mm):
        print("There aren't any records for these dates.")
        sys.exit(2)

    start_date = tz.localize(datetime.strptime(f"{yyyy}-{mm}-01", "%Y-%m-%d"))
    ndays = monthrange(int(yyyy), int(mm))[1]
    end_date = tz.localize(datetime.strptime(f"{yyyy}-{mm}-{ndays}", "%Y-%m-%d"))
    
    # get data from the Lufft and Davis AWS
    # stored in a list for easy iteration if there are future databases to join
    table_name = ['observations_observation', 'observations_mo_observation']
    for table in table_name:
        df = get_data(table, start_date, end_date)
    
        # separate each observation by their station
        unique_ids = df.station_id.unique()
        df_dict = {stn : pd.DataFrame() for stn in unique_ids}

        for key in df_dict.keys():
            # sort each station data by timestamp for easier manipulation later
            df_dict[key] = df[:][df.station_id == key]
            df_dict[key] = df_dict[key].sort_values(by='timestamp')

            # create a monthly and station directory in folder
            out_file = out_dir / f"{yyyy}/{mm}/{file_suffix}-{yyyy}{mm}-{key}.csv"

            out_file.parent.mkdir(parents=True, exist_ok=True)
            df_dict[key].to_csv(out_file, index=False)


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    qc0_splitstation(yyyy,mm)