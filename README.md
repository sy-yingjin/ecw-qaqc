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