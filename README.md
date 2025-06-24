# ecw-qaqc

### Notes:
- rely on `db-tools` for anything to do with the database.
- to run each script, run command `python <file> {yyyy} {mm}` to collect and process data for the concerned year-month observation.

#### Nav:
- `DBTOOLS` - Collection of scripts interacting with the ECW database
- `qc_scripts` - Unedited scripts made by Emily Limlengco for the Lufft AWS
- `bak` - included in `.gitignore` to avoid clutter in the Git repository
- `dump_obs.py` - to extract observation data from `observations_mo_observation` (Davis database)
- `helpers` - Holds essential files like `qc2_config.csv` and `db.py` needed for some of the scripts to run
- `.env` - user authentication for Shaira Sy (intern of the project)

## Quality Check Guide (for any AWS)
` NOTE: Assumes that the database has the appropriate columns for analysis like timestamp, id, qc_level, and station_id `
1. `obs-qc0_splitstn.py` - bypasses `dump_obs.py` and directly retrieves observation data from the database and divides the observation per-station (requires the help of `db.py`) and also returns an updated list of available aws with their id, name, and station_type
2. `obs-qc1_missing.py` - checks the completeness of observation from each station and their missing percentage (requires the help of `stn_type.csv`)
3. `obs-qc2_values.py` - checks the validity of the ranges and cohesion of the data then returns a flagged error, the invalid value and the concerned variable. (requires the help of `qc2_config.csv`)
4. `obs-qc3_hourly.py` - groups and converts each observation into hourly reports with their values averaged. (requires the help of `stn_type.csv`)
5. (optional) `obs-qc4_change.py`

## Quality Check Guide (for Davis AWS)
1. `dump_obs.py` - retrives observation data from the database using PostGreSQL (requires the help of `db.py` and a `.env`)
2. `qc0_obs_splitstn.py` - divides the observations to per-station.
3. `qc1_obs_missingcheck.py` - checks the completeness of each observation entry- returns an observation log of compiled missing percentages for every station of the yyyy mm requested.
4. `qc2_obs_valuecheck.py` - checks the validity of the ranges provided.
5.  (optional) `qc3_obs_changecheck.py`

### Packages found in env folder:
- cffi (1.16.0)
- greenlet (3.0.3)
- Jinja2 (3.1.4)
- MarkupSafe (2.1.5)
- numpy (2.0.0)
- packaging (24.1)
- pandas (2.2.2)
- pip (24.1.2)
- psycopg2 (2.9.9)
- psycparser (2.22)
- python-dateutil (2.9.0.post0)
- python-dotenv (1.0.1)
- pytz (2024.1)
- rpy2 (3.5.16)
- pip
- typing_extensions (4.12.2)
- tzdata (2024.1)
- tzlocal (5.2)
- pytest (8.4.1)
-- colorama (0.4)