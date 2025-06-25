from helpers.qaqc.obs_qc0_splitstn import qc0_splitstation
from helpers.qaqc.obs_qc1_missing import qc1_missing
from helpers.qaqc.obs_qc2_values import qc2_values
from helpers.qaqc.obs_qc3_hourly import qc3_hourly

def test_qc0():
    assert qc0_splitstation()