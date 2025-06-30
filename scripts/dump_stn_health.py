import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from calendar import monthrange
from helpers.db import get_data

tz = pytz.timezone("Asia/Manila")


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
    table_name = "observations_stationhealth"
    file_suffix = "stationhealth"
    out_dir = Path("bak")
    yyyy = sys.argv[1]
    mm = sys.argv[2]

    start_date = tz.localize(datetime.strptime(f"{yyyy}-{mm}-01", "%Y-%m-%d"))
    ndays = monthrange(int(yyyy), int(mm))[1]
    end_date = start_date + timedelta(days=ndays) - timedelta(milliseconds=1)
    df = get_data(table_name, start_date, end_date)

    out_file = out_dir / f"{yyyy}/{file_suffix}-{yyyy}{mm}.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)
