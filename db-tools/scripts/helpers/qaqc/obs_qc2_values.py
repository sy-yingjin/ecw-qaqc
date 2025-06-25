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
    max = config_df.loc[(config_df['var'] == var),'max'].item()
    min = config_df.loc[(config_df['var'] == var),'min'].item()
    return [min, max]


# Prerequisite/s: `obs_qc0_splitstn.py`
def qc2_values(yyyy,mm):
    file_prefix = 'observation'

    # get files from monthly directory 
    main_dir = Path('bak')
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # get the previous log data csv
    check_file = main_dir / f"{yyyy}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"

    # extract data from csv
    check_df = pd.read_csv(check_file, usecols=[
        'qc_level', 'stn_id', 'qc1-missing_perc',
        'qc1-expected_obs', 'qc1-actual_obs'
    ])
    # create new columns for qc2
    check_df['id'] = ''
    check_df['timestamp'] = ''
    check_df['flagged_error'] = ''
    check_df['qc2-flagged_var'] = ''
    check_df['qc2-flagged_data'] = ''

    # loop through the files
    for file in files:
        df = pd.read_csv(file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')

        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501

        print(f"Checking validity of data from station id {stn_id[0]}...")

        '''=========================================
        VALIDITY RANGE CHECKS: Checks for if the data falls within the valid data range
        will raise the `invalid range` flag

        '''
        test_range = ['temp', 'srad', 'pres', 'rh', 'wdir', 'wspd']
        for variable in test_range:
            minmax = get_minmax(file, variable)

            for index, value in df.loc[
                (df[variable] < minmax[0]) | (df[variable] > minmax[1]), variable
            ].items():
                obs_id = df['id'].get(index)

                # store data into the dataframe
                check_df.loc[-1] = [2, stn_id[0],'','','',obs_id,index,'invalid range', variable, value]
                check_df.index += 1
                check_df.sort_index


        '''=========================================
        COHESIVE LOGIC CHECKS: Checks for contradictions or logic between variables
        will raise the `incohesive data` flag
        '''
        # Solar Radiation detected at night:
        for index, value in df.loc[
            (df['srad'] > 0) & ((df.index.hour > 18) | (df.index.hour < 5)), 'srad'
        ].items():
            obs_id = df['id'].get(index)
            
            # store data into the dataframe
            check_df.loc[-1] = [2, stn_id[0],'','','',obs_id,index,'incohesive data', 'srad', value]
            check_df.index += 1
            check_df.sort_index
            
        # Humidity is at 99% without rainfall and (temp-td) is less than 0.2
        for index, value in df.loc[
            ((df['temp'] - df['td']) <= 0.2) & (df['rh'] == 99) & (df['rr'] == 0), 'rh'
        ].items():
            obs_id = df['id'].get(index)
            
            # store data into the dataframe
            check_df.loc[-1] = [2, stn_id[0],'','','',obs_id,index,'incohesive data', 'rh', value]
            check_df.index += 1
            check_df.sort_index

        # Wind Direction exists when Wind Speed is 0
        for index, value in df.loc[
            (df['wdir'].notna()) & (df['wspd'] == 0), 'wdir'
        ].items():
            obs_id = df['id'].get(index)
            
            # store data into the dataframe
            check_df.loc[-1] = [2, stn_id[0],'','','',obs_id,index,'incohesive data', 'wdir', value]
            check_df.index += 1
            check_df.sort_index
            

        # output a csv
        check_file = main_dir / f"{yyyy}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"
        check_file.parent.mkdir(parents=True, exist_ok=True)
        check_df.to_csv(check_file, index=False)

        # mark datapoints as within valid range
        df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 1, other=2)
        df.to_csv(file)


if __name__ == "__main__":
    nargs = len(sys.argv[1:])
    if nargs != 2:
        help_message(nargs)
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    qc2_values(yyyy,mm)