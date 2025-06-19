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

    # get the previous log data csv
    out_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"

    # extract data from csv
    out_df = pd.read_csv(out_file, usecols=[
        'qc_level', 'stn_id', 'qc1-missing_perc',
        'qc1-expected_obs', 'qc1-actual_obs'
    ])
    # create new columns for qc2
    out_df['timestamp'] = ''
    out_df['id'] = ''
    out_df['flagged_error'] = ''
    out_df['qc2-flagged_var'] = ''
    out_df['qc2-flagged_data'] = ''

    # loop through the files
    for file in files:
        df = pd.read_csv(file, index_col=0)
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
                out_df.loc[-1] = [2, stn_id[0],'','','',index,obs_id,'invalid range', variable, value]
                out_df.index += 1
                out_df.sort_index

        # Temperature
        # minmax = get_minmax(file,'temp')
        # # test_range = ['temp', 'srad', 'pres', 'rh', 'wdir', 'wspd']
        # for index, value in df.loc[
        #     (df['temp'] < 15) | (df['temp'] > 40), 'temp'
        # ].items():
        #     obs_id = df['id'].get(index)
        #     print(f" - observed {value} at {stn_id[0]} at time {index}")

        #     # store data into the dataframe
        #     out_df.loc[-1] = [2, stn_id[0],'','','',index,obs_id,'invalid range', 'temp', value]
        #     out_df.index += 1
        #     out_df.sort_index


        '''=========================================
        COHESIVE LOGIC CHECKS: Checks for contradictions or logic between variables
        will raise the `incohesive data` flag
        '''
        # Solar Radiation detected at night:
        for index, value in df.loc[
            (df['srad'] > 0) & ((df['hour'] > 18) | (df['hour'] < 5)), 'srad'
        ].items():
            obs_id = df['id'].get(index)

            # store data into the dataframe
            out_df.loc[-1] = [2, stn_id[0],'','','',index,obs_id,'incohesive data', 'srad', value]
            out_df.index += 1
            out_df.sort_index
            
        # Temperature (temp) - Dewpoint (td) should be greater than 0.2
        for index, value in df.loc[
            ((df['temp'] - df['td']) <= 0.2), 'td'
        ].items():
            obs_id = df['id'].get(index)

            # store data into the dataframe
            out_df.loc[-1] = [2, stn_id[0],'','','',index,obs_id,'incohesive data', 'td', value]
            out_df.index += 1
            out_df.sort_index
            
        # Wind Direction exists when Wind Speed is 0
        for index, value in df.loc[
            (df['wdir'].notna()) & (df['wspd'] == 0), 'wdir'
        ].items():
            obs_id = df['id'].get(index)

            # store data into the dataframe
            out_df.loc[-1] = [2, stn_id[0],'','','',index,obs_id,'incohesive data', 'wdir', value]
            out_df.index += 1
            out_df.sort_index
            

        # output a csv
        out_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(out_file, index=False)

        # mark datapoints as within valid range
        df['qc_level'] = df['qc_level'].mask(df['qc_level'] == 1, other=2)
        df.to_csv(file)