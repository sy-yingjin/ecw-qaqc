import sys
from pathlib import Path


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


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    file_suffix = "observation"
    out_dir = Path("../../bak")
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    print("Running QC0 = Splitting Stations Script... \n")
    obs_qc0_splitstn.qc0_splitstation(yyyy,mm)
    print("Running QC1 = Getting Missing Percentage Script... \n")
    obs_qc1_missing.qc1_missing(yyyy,mm)
    print("Running QC2 = Confirming Observation Values Script... \n")
    obs_qc2_values.qc2_values(yyyy,mm)
    print("Running QC3 = Converting Data to Hourly Reports Scipt... \n")
    obs_qc3_hourly.qc3_hourly(yyyy,mm)
