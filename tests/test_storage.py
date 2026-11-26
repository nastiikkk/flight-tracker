import json

import pytest

from src.aeroplane import Aeroplane
from src.storage import BaseSaver, JSONSaver


@pytest.fixture
def saver(tmp_path):
    file_path = tmp_path / "aeroplanes.json"
    return JSONSaver(str(file_path))


@pytest.fixture
def aeroplane():
    return Aeroplane("AAA111", "Germany", 250.5, 10000.0)


@pytest.fixture
def second_aeroplane():
    return Aeroplane("BBB222", "France", 300.0, 12000.0)


@pytest.fixture
def saved_data(saver, aeroplane, second_aeroplane):
    saver.add_aeroplane(aeroplane)
    saver.add_aeroplane(second_aeroplane)
    return saver


# BaseSaver


def test_base_saver_is_abstract():
    with pytest.raises(TypeError):
        BaseSaver()


def test_json_saver_inherits_base_saver():
    assert issubclass(JSONSaver, BaseSaver)


# read


def test_read_empty_file(saver):
    assert saver.read() == []


def test_read_missing_file(saver):
    assert saver.read() == []


def test_read_valid_json(saver, aeroplane):
    with open(saver.file_path, "w", encoding="utf-8") as file:
        json.dump([aeroplane.to_dict()], file)

    result = saver.read()

    assert result == [aeroplane.to_dict()]


def test_read_invalid_json(saver):
    with open(saver.file_path, "w", encoding="utf-8") as file:
        file.write("invalid json")

    assert saver.read() == []


# check_class_type


def test_check_class_type(saver, aeroplane):
    saver.check_class_type(aeroplane)


def test_check_class_type_invalid_object(saver):
    with pytest.raises(TypeError):
        saver.check_class_type("not an aeroplane")


# add_aeroplane


def test_add_aeroplane(saver, aeroplane):
    saver.add_aeroplane(aeroplane)

    assert saver.read() == [aeroplane.to_dict()]


def test_add_multiple_aeroplanes(saver, aeroplane, second_aeroplane):
    saver.add_aeroplane(aeroplane)
    saver.add_aeroplane(second_aeroplane)

    assert saver.read() == [aeroplane.to_dict(), second_aeroplane.to_dict()]


def test_add_aeroplane_invalid_object(saver):
    with pytest.raises(TypeError):
        saver.add_aeroplane("not an aeroplane")


# delete_aeroplane


def test_delete_aeroplane(saved_data, aeroplane):
    saved_data.delete_aeroplane(aeroplane)

    assert saved_data.read() == [
        {
            "callsign": "BBB222",
            "origin_country": "France",
            "velocity": 300.0,
            "baro_altitude": 12000.0,
        }
    ]


def test_delete_last_aeroplane(saver, aeroplane):
    saver.add_aeroplane(aeroplane)

    saver.delete_aeroplane(aeroplane)

    assert saver.read() == []


def test_delete_aeroplane_invalid_object(saver):
    with pytest.raises(TypeError):
        saver.delete_aeroplane("not an aeroplane")


def test_delete_aeroplane_from_empty_file(saver, aeroplane):
    saver.delete_aeroplane(aeroplane)

    assert saver.read() == []


# get_aeroplanes


def test_get_aeroplanes_by_callsign(saved_data):
    result = saved_data.get_aeroplanes({"callsign": "AAA111"})

    assert len(result) == 1
    assert result[0]["callsign"] == "AAA111"


def test_get_aeroplanes_by_origin_country(saved_data):
    result = saved_data.get_aeroplanes({"origin_country": "France"})

    assert len(result) == 1
    assert result[0]["origin_country"] == "France"


def test_get_aeroplanes_by_velocity(saved_data):
    result = saved_data.get_aeroplanes({"velocity": 250.5})

    assert len(result) == 1
    assert result[0]["callsign"] == "AAA111"


def test_get_aeroplanes_by_altitude(saved_data):
    result = saved_data.get_aeroplanes({"baro_altitude": 12000.0})

    assert len(result) == 1
    assert result[0]["callsign"] == "BBB222"


def test_get_aeroplanes_by_multiple_criteria(saved_data):
    result = saved_data.get_aeroplanes({"origin_country": "Germany", "velocity": 250.5})

    assert len(result) == 1
    assert result[0]["callsign"] == "AAA111"


def test_get_aeroplanes_no_matches(saved_data):
    result = saved_data.get_aeroplanes({"callsign": "UNKNOWN"})

    assert result == []


def test_get_aeroplanes_empty_criteria(saved_data):
    result = saved_data.get_aeroplanes({})

    assert len(result) == 2
