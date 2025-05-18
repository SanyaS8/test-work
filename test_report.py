import pytest
import sys
import os
import json
from io import StringIO
from unittest.mock import patch
from report import Data, main

@pytest.fixture
def sample_csv(tmp_path):
    csv_content = (
        "id,email,name,department,hours_worked,hourly_rate\n"
        "1,alice@example.com,Alice Johnson,Marketing,160,50\n"
        "2,bob@example.com,Bob Smith,Design,150,40\n"
        "3,carol@example.com,Carol Williams,Design,170,60\n"
    )
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    return csv_file

@pytest.fixture
def data(sample_csv):
    return Data(str(sample_csv))

def test_data_init(data):
    assert data.list_of_departments == ["Design", "Marketing"]
    assert data.id == ["id", "1", "2", "3"]
    assert data.email == ["email", "alice@example.com", "bob@example.com", "carol@example.com"]
    assert data.name == ["name", "Alice Johnson", "Bob Smith", "Carol Williams"]
    assert data.department == ["department", "Marketing", "Design", "Design"]
    assert data.hours_worked == ["hours_worked", "160", "150", "170"]
    assert data.hourly_rate == ["hourly_rate", "50", "40", "60"]

def test_data_init_file_not_found(tmp_path, capsys):
    Data(str(tmp_path / "nonexistent.csv"))
    captured = capsys.readouterr()
    assert "Ошибка: файл не найден" in captured.out

def test_data_init_invalid_format(tmp_path):
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("id,email,name\n1,alice@example.com,Alice")
    with pytest.raises(SystemExit):
        Data(str(invalid_csv))

def test_payout_output(data, capsys):
    data.payout()
    captured = capsys.readouterr()
    output = captured.out
    assert "name" in output
    assert "Alice Johnson" in output
    assert "Bob Smith" in output
    assert "Carol Williams" in output
    assert "Marketing" in output
    assert "Design" in output
    assert "Total: 8000" in output  
    assert "Total: 16200" in output  
    assert "Отчет о выплате зарплат создан." in output

def test_create_payout_report(data, tmp_path):
    os.chdir(tmp_path)
    data.filename = "test.csv"
    data.create_payout_report()
    report_path = tmp_path / "payout_report(test.csv).json"
    assert report_path.exists()
    
    with open(report_path, "r") as file:
        report_data = json.load(file)
    
    assert len(report_data) == 2
    assert report_data[0]["department"] == "Design"
    assert len(report_data[0]["employees"]) == 2
    assert report_data[0]["employees"][0]["name"] == "Bob Smith"
    assert report_data[0]["employees"][1]["name"] == "Carol Williams"
    assert report_data[0]["total:"] == 16200
    assert report_data[1]["department"] == "Marketing"
    assert len(report_data[1]["employees"]) == 1
    assert report_data[1]["employees"][0]["name"] == "Alice Johnson"
    assert report_data[1]["total:"] == 8000

def test_empty_csv(tmp_path):
    csv_content = "id,email,name,department,hours_worked,hourly_rate\n"
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(csv_content)
    os.chdir(tmp_path)
    data = Data(str(csv_file))
    data.create_payout_report()
    report_path = tmp_path / "payout_report(empty.csv).json"
    assert report_path.exists()
    with open(report_path, "r") as file:
        report_data = json.load(file)
    assert report_data == []

def test_main_valid_args(sample_csv, tmp_path, capsys):
    os.chdir(tmp_path)
    with patch("sys.argv", ["report.py", str(sample_csv), "--report", "payout"]):
        main()
        captured = capsys.readouterr()
        assert "Отчет о выплате зарплат создан." in captured.out
        report_path = tmp_path / "payout_report(test.csv).json"
        assert report_path.exists()

def test_main_no_report_arg(capsys):
    with patch("sys.argv", ["report.py", "test.csv"]), pytest.raises(SystemExit):
        main()
        captured = capsys.readouterr()
        assert "Ошибка: не указан параметр --report" in captured.out

def test_main_unknown_report(sample_csv, capsys):
    with patch("sys.argv", ["report.py", str(sample_csv), "--report", "invalid"]), pytest.raises(SystemExit):
        main()
        captured = capsys.readouterr()
        assert "Ошибка: неизвестный тип отчета invalid" in captured.out

def test_main_nonexistent_file(tmp_path, capsys):
    nonexistent_file = tmp_path / "nonexistent.csv"
    with patch("sys.argv", ["report.py", str(nonexistent_file), "--report", "payout"]):
        main()
        captured = capsys.readouterr()
        assert f"Ошибка: файл {os.path.basename(str(nonexistent_file))} не существует" in captured.out