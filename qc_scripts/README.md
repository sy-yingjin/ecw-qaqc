These six scripts are designed to be used in conjunction with dump_obs.py (courtesy of sir Emil) to access the online Lufft database and check the datapoints for QAQC. dump_obs.py saves the observations in a folder within the scripts folder named bak, and this is where the process begins. In the order they need to be run (* meaning optional): 

 1. qc0_split_obs.py - This script splits the main observation file (observation-yyyymm.csv) into per station files for ease of checking. It also creates a new monthly directory within the yearly one. 
 2. qc1_timestamp_obs.py - This script fits the data to a uniform time series index for ease of checking later. It also checks for completeness of data and creates the log file (observation-yyyymm-id-log.txt), placing it in a new station-specific folder within the monthly directory.
 3. qc2_rangevalues_obs.py - This script checks if the datapoints are within the valid range, flagging them on the log file if they aren't. 
 4. qc3_stepvalues_obs.py - This script checks if the temporal distances between datapoints are within the valid range, flagging them on the log file if they aren't. 
 5. qc4_statvalues_obs.py* - This script contains optional statistical checks that verify the deviation of certain values over specific periods of time. 
 6. qc5_plotvalues_obs.py - This script plots the data points, allowing for visual checks. It also moves the csvs to inside their respective station folders, so if checks are to be run again they must start from 0. 

Running all the scripts in the command line uses the syntax 'python script_name.py yyyy mm', adapted from dump_obs.py. All scripts were adapted from ma'am Erica's R scripts: 
Bañares, Erica. Regional Climate Systems Laboratory, Manila Observatory (2024) AWSdataQAQC (Version 2) [R]. https://rcs.observatory.ph/git/ebanares/AWSdataQAQC/scripts/Version 2