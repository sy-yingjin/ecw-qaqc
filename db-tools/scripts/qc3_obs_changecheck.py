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

    # indicate the date of log retrieval if there are files to log
    if files:
        log = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-qc2-log.txt"
        log.parent.mkdir(parents=True, exist_ok=True)

    # open file for logging while checks run
    with open(log, 'w') as f:

        f.write("===LEVEL 3: STEP VALUE CHECKS===\n")
        f.write("Datapoints with time-based differences outside valid range by station:\n\n")

        # loop through the files
        for file in files:
            df = pd.read_csv(file, index_col=0)
            stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501

            # Convert timestamp to datetime object
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            print(f"Checking validity of data from station id {stn_id[0]}...")


            