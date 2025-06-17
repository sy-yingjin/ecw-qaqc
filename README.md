# ecw-qaqc

## Quality Level Guide
1. `qc0_obs_splitstn.py` - divides the observations to per-station.
2. `qc1_obs_missingcheck.py` - checks the completeness of each observation entry- returns an observation log of compiled missing percentages for every station of the yyyy mm requested.
3. `qc2_obs_valuecheck.py` - checks the validity of the ranges provided.
4. `qc3_obs_changecheck.py` - checks the validity of the change rate between observation entries.

### Notes:
- rely on `db-tools` for anything to do with the database.

### Nav:
- `DBTOOLS` - Collection of scripts interacting with the ECW database
- `qc_scripts` - Unedited scripts made by Emily Limlengco for the Lufft AWS
- `bak` - included in `.gitignore` to avoid clutter in the Git repository

### Scripts/Files Edited:
- `.env` - user authentication for Shaira Sy (intern of the project)
- `dump_obs.py` - to extract observation data from `observations_mo_observation` (Davis database)

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