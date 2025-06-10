import sys
import os
import glob
import re 

import pandas as pd 

import matplotlib.pyplot as plt

from pathlib import Path
from calendar import monthrange


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

        # make plots 
        ndays = monthrange(int(yyyy),int(mm))[1]
        idx = pd.date_range(    
            start=pd.to_datetime("00:00"),
            end=pd.to_datetime("23:50"), 
            freq='10min',                
            tz='Asia/Manila',
        ).time
            
        print(f"plotting values for station id {stn_id[0]}...")

        # plotting temperature 
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['temp'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        temp_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        temp_plt = temp_by_day.plot(
            kind='line', 
            title=f'Temperature by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='temperature in Celsius',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/temp-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        # plotting dewpoint 
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['td'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        td_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        td_plt = td_by_day.plot(
            kind='line', 
            title=f'Dew Point Temperature by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='temperature in Celsius',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/dewpoint-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        # plotting pressure 
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['pres'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        pres_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        pres_plt = pres_by_day.plot(
            kind='line', 
            title=f'Atmospheric Pressure by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='pressure in mbar',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/pressure-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        # plotting wind speed 
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['wspd'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        wspd_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        wspd_plt = wspd_by_day.plot(
            kind='line', 
            title=f'Wind Speed by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='speed in km/hr',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/windspeed-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        # plotting humidity
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['rh'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        rh_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        rh_plt = rh_by_day.plot(
            kind='line', 
            title=f'Atmospheric Pressure by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='humidity in percentage',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/humidity-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        # plotting solar radiation 
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['srad'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        srad_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        srad_plt = srad_by_day.plot(
            kind='line', 
            title=f'Solar Radiation by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='radiation in Wh/m^2',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/solarradiation-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        # plotting pressure 
        plt_dict = {} 
        for i in range(ndays): 
            loop_df = pd.DataFrame(data=df['rr'].iloc[i*144:(i+1)*144].values, index=idx)
            plt_dict[f'{i+1}/{mm}/{yyyy}'] = loop_df
        rr_by_day = pd.concat(plt_dict.values(), axis=1, keys=plt_dict.keys())

        rr_plt = rr_by_day.plot(
            kind='line', 
            title=f'Rainfall Rate by Day for Station {stn_id[0]}', 
            figsize=(24,12),
            colormap='tab20c',
            xticks=idx,
            rot=75,
            ylabel='rainfall in mm',
        )
        plt_file = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/rainfall-{yyyy}{mm}-{stn_id[0]}.png"
        plt.legend(plt_dict.keys(),loc='center left', bbox_to_anchor=(1.0, 0.5)) 
        plt.savefig(plt_file)
        plt.close()

        in_folder = main_dir / f"{yyyy}/{mm}/{stn_id[0]}/{file_prefix}-{yyyy}{mm}-{stn_id[0]}.csv"
        os.rename(file, in_folder) 