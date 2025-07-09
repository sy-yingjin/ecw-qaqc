import os
import glob
import re
import pandas as pd

from pathlib import Path


# GLOBAL VARIABLES
file_prefix = "observation"
main_dir = Path("bak")
config_dir = Path("helpers")

config_file = config_dir / "qc4_config.csv"


#  TO-DO: what to do if there are multiple checks for the same variable (hourly vs 12-hourly or 1 day)
def get_period_diff(config_file: Path, var: str) -> tuple[int, float]:
    try:
        # extract data from csv
        config_df = pd.read_csv(config_file, usecols=["var", "period", "diff"])

        if var not in config_df["var"].to_numpy(dtype=str):
            raise ValueError

        period = config_df.loc[(config_df["var"] == var), "period"].item()
        diff = config_df.loc[(config_df["var"] == var), "diff"].item()

        return period, diff
    except FileNotFoundError:
        print("Can't locate the Configuration file")
    except ValueError:
        print("Unrecognized Variable Found")
    except:  # noqa: E722
        print("Something went wrong with getting the MinMax of Range Checking")


def get_diff(df: pd.DataFrame, stn_id: int, check_df: pd.DataFrame) -> pd.DataFrame:
    try:
        # these varialbes are expected to be found in the CSV file
        test_range = []
        for variable in test_range:
            if variable not in df.columns:
                raise ValueError

            period, diff = get_period_diff(config_file, variable)

            diff_df = df[variable].diff(periods=period)
            for index, value in diff_df[(diff_df > diff) | (diff_df < -diff)].items():
                # store data into the dataframe
                check_df.loc[-1] = [
                    4,
                    stn_id,
                    "",
                    "",
                    "",
                    "",
                    index,
                    "invalid rate",
                    "",
                    "",
                    variable,
                    value,
                ]
                check_df.index += 1
                check_df.sort_index

        return check_df

    except ValueError:
        print("The column you're asking for doesn't exist")
    except:  # noqa: E722
        print("Something went wrong with testing the change rate")


def qc4_change(yyyy: int, mm: int):
    # get files from monthly directory
    files = glob.glob(os.path.join(main_dir, f"{yyyy}/{mm}/*.csv"))

    # get the previous log data csv
    check_file = main_dir / f"{yyyy}/{mm}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"

    # extract data from csv
    check_df = pd.read_csv(
        check_file,
        usecols=[
            "qc_level",
            "stn_id",
            "qc1-missing_perc",
            "qc1-expected_obs",
            "qc1-actual_obs",
            "id",
            "timestamp",
            "flagged_error",
            "qc2-flagged_var",
            "qc2-flagged_data",
        ],
    )

    # create new columns for qc4
    check_df["qc4-flagged_var"] = ""
    check_df["qc4-flagged_data"] = ""

    # loop through the files
    for file in files:
        df = pd.read_csv(file)

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")

        stn_id = re.findall(f"{yyyy}{mm}-([\\d]+).csv", os.path.basename(file))  # noqa: E501

        print(f"Checking validity of data from station id {stn_id[0]}...")

        """=========================================
        CHANGE RATE CHECKS: Checks the temporal difference or sum of variables
        will raise the `invalid_rate` flag
        """
        check_df = get_diff(df, int(stn_id[0]), check_df)

        # output a csv
        check_file = main_dir / f"{yyyy}/obs_logs/{file_prefix}-{yyyy}{mm}-log.csv"
        check_df = df.to_csv(check_file, index=False)

        # mark datapoints as within valid range
        df["qc_level"] = df["qc_level"].mask(df["qc_level"] == 3, other=4)
        df.to_csv(file)
