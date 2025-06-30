from pathlib import Path
from datetime import datetime
import pytz

import pandas as pd

from helpers.db import DB_BAK_ENGINE

tz = pytz.timezone("Asia/Manila")


if __name__ == "__main__":
    file_suffix = "station"
    out_dir = Path("bak")

    sql_query = """SELECT *
        FROM observations_station
        ORDER BY id"""
    df = pd.read_sql(sql_query, DB_BAK_ENGINE)

    ts = datetime.now()
    out_file = out_dir / f"stn/{file_suffix}-{ts:%Y%m%d%H}.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)
