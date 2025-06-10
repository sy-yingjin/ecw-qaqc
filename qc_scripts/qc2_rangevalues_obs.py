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

    # loop through files
    for file in files: 
        df = pd.read_csv(file, index_col=0)
        stn_id = re.findall(f"{yyyy}{mm}-(\d+).csv", os.path.basename(file))
        print(f"checking range values for station id {stn_id[0]}...")
        log = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/{file_prefix}-{yyyy}{mm}-{stn_id[0]}-log.txt"
        # open file for logging while checks are run
        with open(log, 'a') as f:
            f.write("\n===LEVEL 2: RANGE VALUE CHECKS===\nDatapoints outside valid range:\n")

            # checking temperature (15C <= temp <= 40C)
            f.write("\nTimestamps where temperature outside accepted range (between 15 - 40 degrees Celsius):\n")
            for index, value in df.loc[(df['temp'] < 15) | (df['temp'] > 40), 'temp'].items(): 
                f.write(f" - observed {value} C on {index}\n")

            # checking dew point (td => temp, 10C <= td)
            f.write("\nTimestamps where dew point temperature outside accepted range or greater than ambient temperature (below 10 degrees Celsius):\n")
            for index, value in df.loc[(df['td'] > df['temp']) | (df['td'] < 10), 'td'].items(): 
                f.write(f" - observed {value} C on {index}\n")

            # checking solar radiation (0W/m^2 <= srad <= 1200W/m^2)
            f.write("\nTimestamps where solar radiation outside accepted range (between 0 - 1200 W/m^2):\n")
            for index, value in df.loc[(df['srad'] < 0) | (df['srad'] > 1200), 'srad'].items(): 
                f.write(f" - observed {value} W/m^2 on {index}\n")

            f.write("\nTimestamps where solar radiation observed at nighttime (after 1800 and before 0500 hours):\n")
            for index, value in df.loc[(df['srad'] > 0) & ((df['time'] > 18) | (df['time'] < 5)), 'srad'].items(): 
                f.write(f" - observed {value} W/m^2 on {index}\n")

            # checking pressure (940mbar <= pres <= 1060mbar)
            f.write("\nTimestamps where pressure outside accepted range (between 940 - 1600 mbar):\n")
            for index, value in df.loc[(df['pres'] < 940) | (df['pres'] > 1600), 'pres'].items(): 
                f.write(f" - observed {value} mbar on {index}\n")

            # checking humidity (50% <= rh <= 100%)
            f.write("\nTimestamps where relative humidity outside accepted range (between 50 - 100%):\n")
            for index, value in df.loc[(df['rh'] < 50) | (df['rh'] > 100), 'rh'].items(): 
                f.write(f" - observed {value}% on {index}\n")

            # checking rainfall rate (rr <= 20)
            f.write("\nTimestamps where rainfall rate outside accepted range (below 20 mm):\n")
            for index, value in df.loc[(df['rr'] > 20), 'rr'].items(): 
                f.write(f" - observed {value} mm on {index}\n")

            # checking wind direction and wind speed (0 <= wdir <= 360, wspd(x) <= 90)
            f.write("\nTimestamps where wind direction observed for 0 km/hr wind speed:\n")
            for index, value in df.loc[(df['wdir'] > 0) & (df['wspd'] == 0), 'wdir'].items(): 
                f.write(f" - observed {value} degrees on {index}\n")

            f.write("\nTimestamps where wind direction oustide accepted range (between 0 and 360 degrees):\n")
            for index, value in df.loc[(df['wdir'] < 0) | (df['wspd'] > 360), 'wdir'].items(): 
                f.write(f" - observed {value} degrees on {index}\n")
            
            f.write("\nTimestamps where wind speed outside accepted range (below 90 km/hr):\n")
            for index, value in df.loc[df['wspd'] > 90, 'wspd'].items(): 
                f.write(f" - observed {value} km/hr on {index}\n")

            f.write("\nTimestamps where max wind speed outside accepted range (below 90 km/hr):\n")
            for index, value in df.loc[df['wspdx'] > 90, 'wspdx'].items(): 
                f.write(f" - observed {value} km/hr on {index}\n")

            # mark datapoints as within valid range
            df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 1, other=2)

            df.to_csv(file)