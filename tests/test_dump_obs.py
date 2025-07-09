import pytest

from dump_obs import help_message


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
