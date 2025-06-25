import sys
import pandas as pd
from pathlib import Path
from datetime import datetime


from helpers.qaqc import obs_qc0_splitstn
from helpers.qaqc import obs_qc1_missing
from helpers.qaqc import obs_qc2_values
from helpers.qaqc import obs_qc3_hourly


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


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    file_suffix = "observation"
    out_dir = Path("../../bak")
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    # is the requested year and month valid?
    if validate_request(yyyy,mm):
        print("There aren't any records for these dates.")
        sys.exit(2)

    print("\nRunning QC0 = Splitting Stations Script... \n")
    obs_qc0_splitstn.qc0_splitstation(yyyy,mm)
    print("\nRunning QC1 = Getting Missing Percentage Script... \n")
    obs_qc1_missing.qc1_missing(yyyy,mm)
    print("\nRunning QC2 = Confirming Observation Values Script... \n")
    obs_qc2_values.qc2_values(yyyy,mm)
    print("\nRunning QC3 = Converting Data to Hourly Reports Scipt... \n")
    obs_qc3_hourly.qc3_hourly(yyyy,mm)
