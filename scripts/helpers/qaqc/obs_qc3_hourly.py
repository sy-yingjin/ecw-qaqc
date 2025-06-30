import sys
import os
import glob
import re
import pandas as pd

from datetime import datetime
from pathlib import Path


def help_message(nargs):
    if nargs == 0:
        print("missing `year` parameter")
    if nargs < 2:
        print("missing `month` parameter")
    print(f"{sys.argv[0]} yyyy mm")
    sys.exit(2)

def validate_request(yyyy,mm):
    try:
        input_date = pd.to_datetime(datetime.strptime(f"{yyyy}-{mm}-01", "%Y-%m-%d")).tz_localize('Asia/Manila')
        current_date = pd.to_datetime(datetime.now()).tz_localize('Asia/Manila')
        lim_date = pd.to_datetime(datetime.strptime("2010-01-01", "%Y-%m-%d")).tz_localize('Asia/Manila')

        return (input_date < lim_date) or (input_date > current_date)
    except:  # noqa: E722
        print("The requested `yyyy` and `mm` isn't possible.")

"""def get_stn_type(id):
    stn_dir = Path('bak')
    stn_file = stn_dir / "stn-type.csv"

    # extract data from stn csv
    stn_df = pd.read_csv(stn_file, usecols=[
        'id', 'station_type'
    ])
    aws = stn_df.loc[(stn_df['id'] == (id)),'station_type'].item()
    return aws"""


# Running this file will before qc1 and qc2 will make their reports inaccurate
def qc3_hourly(yyyy,mm):

    # is the requested year and month valid?
    if validate_request(yyyy,mm):
        print("There aren't any records for these dates.")
        sys.exit(2)

    # get files from monthly directory
    main_dir = Path('bak')
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))


    # loop through the files
    for file in files:
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501

        print(f"Converting data to hourly reports for station id {stn_id[0]}...")

        # get columns excluding station_id, id created_on and updated_on
        # The observation data is from a Davis AWS
        col_MO = [
                'timestamp',
                'pres', 'rr', 'rh', 'temp', 'td', 'wdir',
                'wspd', 'wspdx', 'srad', 'hi', 'wchill',
                'rain', 'tx', 'tn', 'wrun', 'thwi', 'thswi',
                'senergy','sradx', 'uvi', 'uvdose',
                'uvx', 'hdd', 'cdd', 'et', 'wdirx',
            ]
        
        # The observation data is from a Lufft AWS
        col_SMS = [
                'timestamp',
                'pres','rr','rh','temp','td','wdir','wspd',
                'wspdx','srad','mslp','hi','wchill',
            ]
        
        # matching column data
        col_names = [x for x in col_SMS if x in col_MO]

        df = pd.read_csv(file, usecols=col_names)
        df = df[col_names]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort the main observation dataframe to an hourly state
        # all observations will be averaged
        hourly_df = df.groupby(pd.Grouper(key='timestamp',freq='h'))[col_names[1:]].mean().round(2)
        hourly_df.insert(0, 'qc_level', 3)

        # output a csv
        hourly_df.to_csv(file)


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    qc3_hourly(yyyy,mm)