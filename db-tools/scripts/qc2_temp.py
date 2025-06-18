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

# get the configuration for min-max values
def get_minmax(file, var):
    help_dir = Path('helpers')
    config_file = help_dir / "qc2_config.csv"

    # extract data from csv
    config_df = pd.read_csv(config_file, usecols=[
        'var','min','max'
    ])

    max = config_df.loc[(config_df['var'] == var), 'max'].iloc[0]
    min = config_df.loc[(config_df['var'] == var), 'min'].iloc[0]

    print(f"{var}'s max is {max} and min is {min}")

    return [min, max]


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

    # # get the previous log data csv
    # out_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"

    # # extract data from csv
    # out_df = pd.read_csv(out_file, usecols=[
    #     'stn_id', 'qc_level'
    # ])


    # indicate the date of log retrieval if there are files to log
    if files:
        log = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-qc2-log.txt"
        log.parent.mkdir(parents=True, exist_ok=True)


# loop through the files
    for file in files:
        df = pd.read_csv(file, index_col=0)
        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501

        print(f"Checking validity of data from station id {stn_id[0]}...")

        # open file for logging while checks run
        with open(log, 'w') as f:

            f.write("===LEVEL 2: RANGE VALUE CHECKS===\nDatapoints outside valid range:\n\n")
            f.write(f"\n\n\nOBSERVATIONS FLAGGED FROM STATION ID# {stn_id[0]}\n\n")


            # Temperature: flagged if < 15C or > 40C
            f.write("\nTimestamps where temperature outside accepted range (15C < temp < 40C):\n")
            minmax = get_minmax(file, 'temp')
            for index, value in df.loc[
                (df['temp'] < minmax[0]) | (df['temp'] > minmax[1]), 'temp'
            ].items():
                f.write(f" - observed {value}C on {index}\n")
            

            # Solar Radiation: flagged if < 0 or > 1200
            f.write("\nTimestamps where solar radiation is outside accepted range (0 W/m^2 < srad < 1200 W/m^2):\n")
            for index, value in df.loc[
                (df['srad'] < 0) | (df['srad'] > 1200), 'srad'
            ].items(): 
                f.write(f" - observed {value} W/m^2 on {index}\n")
            
            # Solar Radiation: flagged if not NA at 7pm-5am
            # i.e. 1800 - 0500
            f.write("\nTimestamps where solar radiation is observed at nighttime (7pm-5am):\n")
            for index, value in df.loc[
                (df['srad'] > 0) & ((df['hour'] > 18) | (df['hour'] < 5)), 'srad'
            ].items():
                f.write(f" - observed {value} W/m^2 on {index}\n")


            # Pressure: flagged if < 990mb or > 1020mb
            f.write("\nTimestamps where pressure is outside accepted range (990mb < pres < 1020mb):\n")
            for index, value in df.loc[
                (df['pres'] < 990) | (df['pres'] > 1020), 'pres'
            ].items(): 
                f.write(f" - observed {value} mb on {index}\n")


            # Humidity: flagged if < 0% or > 100%
            f.write("\nTimestamps where relative humidity is outside accepted range (0% < rh < 100%):\n")
            for index, value in df.loc[
                (df['rh'] < 0) | (df['rh'] > 100), 'rh'
            ].items(): 
                f.write(f" - observed {value}% on {index}\n")

            # Humidity: flag if 99% but rainfall is NA
            f.write("\nTimestamps where relative humidity is high even though rainfall is undetected:\n")
            for index, value in df.loc[
                (df['rh'] == 99) & ((df['rr'].isna()) | (df['rr'] == 0)), 'rh'
            ].items():
                f.write(f" - observed {value}% on {index}\n")


            # Wind Speed: flagged if < 0km/hr > 90km/hr
            f.write("\nTimestamps where wind speed is outside accepted range (0 km/hr < wspd < 90 km/hr):\n")
            for index, value in df.loc[
                (df['wspd'] < 0) | (df['wspd'] > 90), 'wspd'
            ].items():
                f.write(f" - observed {value} degrees on {index}\n")


            # Wind Direction: flagged if < 0deg or > 360deg
            f.write("\nTimestamps where wind direction is outside accepted range (0deg < wdir < 360deg):\n")
            for index, value in df.loc[
                (df['wdir'] < 0) | (df['wdir'] > 360), 'wdir'
            ].items(): 
                f.write(f" - observed {value} degrees on {index}\n")

            # Wind Direction: flag if exists but wspd = 0
            f.write("\nTimestamps where wind direction exists when wind speed is undetected/zero:\n")
            for index, value in df.loc[
                ((df['wdir'].notna()) | (df['wdir'] > 0)) & (df['wspd'] == 0), 'wdir'
            ].items():
                f.write(f" - observed {value} degrees on {index}\n")

            # mark datapoints as within valid range
            df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 1, other=2)

            df.to_csv(file)