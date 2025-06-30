import pytest
import pandas as pd

from obs_qaqc import help_message, validate_request
from helpers.qaqc.obs_qc1_missing import get_stn_type,get_matching_columns,get_frequency,qc1_file_pass
from helpers.qaqc.obs_qc2_values import get_minmax


def test_help_message_no_args(mocker, capsys):
    script_name = "script.py"
    mocker.patch("sys.argv", [script_name])
    with pytest.raises(SystemExit) as e:
        help_message(0)
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "missing `year` parameter" in captured.out
    assert "missing `month` parameter" in captured.out
    assert f"{script_name} yyyy mm" in captured.out

def test_help_message_one_arg(mocker, capsys):
    script_name = "script.py"
    mocker.patch("sys.argv", [script_name])
    with pytest.raises(SystemExit) as e:
        help_message(1)
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "missing `month` parameter" in captured.out
    assert f"{script_name} yyyy mm" in captured.out

def test_validate_request_failed(capsys):
    # current valid ranges: 2010+
    list_yy = [1999, 2000, 2001]
    for year in list_yy:
        with pytest.raises(SystemExit) as e:
            validate_request(year,"12")
        assert e.value.code == 2
        captured = capsys.readouterr()
        assert "The requested `yyyy` and `mm` isn't possible." in captured.out
    # valid date
    assert validate_request(2020,"02") is None

def test_get_stn_type(mocker,capsys):
    mock_df = mocker.Mock()
    mock_df = pd.DataFrame({'id': [9,5001], 'station_type': ['SMS','MO']})
    mock_csv = mocker.patch('pandas.read_csv', return_value=mock_df)
    assert get_stn_type('dummy.csv',9) == "SMS"
    mock_csv.assert_called_once_with("dummy.csv", usecols=['id','station_type'])
    assert get_stn_type('dummy.csv',5001) == "MO"

    mock_csv = mocker.patch('pandas.read_csv', side_effect=ValueError)
    assert get_stn_type('dummy.csv',1) is None
    mock_csv = mocker.patch('pandas.read_csv', side_effect=FileNotFoundError)
    assert get_stn_type('dummy.csv',9) is None

    captured = capsys.readouterr()
    # for ValueError
    assert "Unrecognized Station ID Found" in captured.out
    # for FNFError
    assert "Can't locate the Station List file" in captured.out

def test_get_minmax(mocker,capsys):
    mock_df = mocker.Mock()
    mock_df = pd.DataFrame({'var': ['temp','wdir'], 'min': [15,0], 'max': [40,360]})
    mock_csv = mocker.patch('pandas.read_csv', return_value=mock_df)
    assert get_minmax("dummy.csv","temp") == [15, 40]
    mock_csv.assert_called_once_with("dummy.csv", usecols=['var','min','max'])
    assert get_minmax("dummy.csv","wdir") == [0, 360]

    mock_csv = mocker.patch('pandas.read_csv', side_effect=ValueError)
    assert get_minmax("dummy.csv","unknown") is None
    mock_csv = mocker.patch('pandas.read_csv', side_effect=FileNotFoundError)
    assert get_minmax("dummy.csv","temp") is None

    captured = capsys.readouterr()
    # for ValueError
    assert "Unrecognized Variable Found" in captured.out
    # for FNFError
    assert "Can't locate the Configuration file" in captured.out