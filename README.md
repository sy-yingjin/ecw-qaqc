# ecw-qaqc

### Notes:
- rely on `db-tools` for anything to do with the database.
- to run each script, run command `python <file> {yyyy} {mm}` to collect and process data for the concerned year-month observation.

#### Nav:
- `DBTOOLS` - Collection of scripts interacting with the ECW database
- `qc_scripts` - Unedited scripts made by Emily Limlengco for the Lufft AWS
- `bak` - included in `.gitignore` to avoid clutter in the Git repository
- `dump_obs.py` - to extract observation data from `observations_mo_observation` (Davis database)
- `helpers` - Directory that holds essential files like `qc2_config.csv` and `db.py` needed for some of the scripts to run
- `qaqc` - Directory that holds the scripts for quality checking the Lufft and Davis AWS
- `.env` - user authentication to access the database

## Quality Check Guide (for any AWS)
` NOTE: Assumes that the database has the appropriate columns for analysis like timestamp, id, qc_level, and station_id `
1. `obs-qc0_splitstn.py` - bypasses `dump_obs.py` and directly retrieves observation data from the database and divides the observation per-station (requires the help of `db.py`) and also returns an updated list of available aws with their id, name, and station_type
2. `obs-qc1_missing.py` - checks the completeness of observation from each station and their missing percentage (requires the help of `stn_type.csv`)
3. `obs-qc2_values.py` - checks the validity of the ranges and cohesion of the data then returns a flagged error, the invalid value and the concerned variable. (requires the help of `qc2_config.csv`)
4. `obs-qc3_hourly.py` - groups and converts each observation into hourly reports with their values averaged. (requires the help of `stn_type.csv`)
5. (optional) `obs-qc4_change.py`

### Expected Outputs:
1. `{yyyy}/{mm}` - would include the hourly reports of each individual AWS available in `.csv` files.
2. `{yyyy}/obs_logs` - would include the observation logs and reports of the missing percentage and flagged data found in the observation data. stored in `.csv` files by each year and month.


### Packages found in env folder:
- cffi (1.17.1)
- colorama (0.4.6)
- greenlet (3.2.3)
- Jinja2 (3.1.6)
- MarkupSafe (3.0.2)
- numpy (2.3.0)
- packaging (25.0)
- pandas (2.3.0)
- pip (25.1.1)
- pluggy (1.6.0)
- psycopg2 (2.9.10)
- psycopg2-binary (2.9.10)
- psycparser (2.22)
- Pygments (2.19.2)
- pytest (8.4.1)
- pytest-mock (3.14.1)
- python-dateutil (2.9.0.post0)
- python-dotenv (1.1.0)
- pytz (2025.2)
- rpy2 + interface + objects (3.6.1)
- six (1.17.0)
- SQLAlchemy (2.0.41)
- typing_extensions (4.14.0)
- tzdata (2025.5)
- tzlocal (5.3.1)