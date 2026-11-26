
import pytest

from src.aeroplane import Aeroplane


@pytest.fixture
def aeroplane():
    return Aeroplane(
        'AAA111',
        'United States',
        250.5,
        10000.0
    )


# __init__ and properties


def test_aeroplane_init(aeroplane):
    assert aeroplane.callsign == 'AAA111'
    assert aeroplane.origin_country == 'United States'
    assert aeroplane.velocity == 250.5
    assert aeroplane.baro_altitude == 10000.0


@pytest.mark.parametrize(
    'callsign',
    [123, None, True, []]
)
def test_aeroplane_invalid_callsign(callsign):
    with pytest.raises(TypeError):
        Aeroplane(callsign, 'Germany', 250, 10000)


@pytest.mark.parametrize(
    'origin_country',
    [123, None, True, []]
)
def test_aeroplane_invalid_origin_country(origin_country):
    with pytest.raises(TypeError):
        Aeroplane('AAA111', origin_country, 250, 10000)


@pytest.mark.parametrize(
    'velocity',
    ['250', None, [], {}]
)
def test_aeroplane_invalid_velocity(velocity):
    with pytest.raises(TypeError):
        Aeroplane('AAA111', 'Germany', velocity, 10000)


def test_aeroplane_negative_velocity():
    with pytest.raises(ValueError):
        Aeroplane('AAA111', 'Germany', -1, 10000)


@pytest.mark.parametrize(
    'baro_altitude',
    ['10000', None, [], {}]
)
def test_aeroplane_invalid_baro_altitude(baro_altitude):
    with pytest.raises(TypeError):
        Aeroplane('AAA111', 'Germany', 250, baro_altitude)


def test_aeroplane_zero_velocity():
    aeroplane = Aeroplane('AAA111', 'Germany', 0, 10000)

    assert aeroplane.velocity == 0


def test_aeroplane_negative_altitude():
    aeroplane = Aeroplane('AAA111', 'Germany', 250, -100)

    assert aeroplane.baro_altitude == -100


# cast_to_object_list


def test_cast_to_object_list():
    data = {
        'states': [
            [
                'AAA111',  # callsign
                None,
                'United States',  # origin_country
                None,
                None,
                None,
                None,
                10000.0,  # baro_altitude
                None,
                250.5  # velocity
            ]
        ]
    }

    result = Aeroplane.cast_to_object_list(data)

    assert len(result) == 1
    assert isinstance(result[0], Aeroplane)
    assert result[0].callsign == 'AAA111'
    assert result[0].origin_country == 'United States'
    assert result[0].baro_altitude == 10000.0
    assert result[0].velocity == 250.5


def test_cast_to_object_list_empty_states():
    result = Aeroplane.cast_to_object_list({'states': []})

    assert result == []


def test_cast_to_object_list_missing_states():
    result = Aeroplane.cast_to_object_list({})

    assert result == []


@pytest.mark.parametrize(
    'missing_index',
    [0, 2, 7, 9]
)
def test_cast_to_object_list_skips_none_values(missing_index):
    state = [
        'AAA111',
        None,
        'United States',
        None,
        None,
        None,
        None,
        10000.0,
        None,
        250.5
    ]

    state[missing_index] = None

    result = Aeroplane.cast_to_object_list({
        'states': [state]
    })

    assert result == []


def test_cast_to_object_list_multiple_aeroplanes():
    data = {
        'states': [
            [
                'AAA111', None, 'Germany', None, None,
                None, None, 10000.0, None, 250.0
            ],
            [
                'BBB222', None, 'France', None, None,
                None, None, 12000.0, None, 300.0
            ]
        ]
    }

    result = Aeroplane.cast_to_object_list(data)

    assert len(result) == 2
    assert result[0].callsign == 'AAA111'
    assert result[1].callsign == 'BBB222'


# check_class_type


def test_check_class_type(aeroplane):
    other = Aeroplane('BBB222', 'Germany', 200, 9000)

    aeroplane.check_class_type(other)


def test_check_class_type_invalid_object(aeroplane):
    with pytest.raises(TypeError):
        aeroplane.check_class_type('not an aeroplane')


# compare_velocity


def test_compare_velocity_first_is_faster():
    first = Aeroplane('AAA111', 'Germany', 300, 10000)
    second = Aeroplane('BBB222', 'France', 250, 12000)

    assert first.compare_velocity(second) is True


def test_compare_velocity_first_is_slower():
    first = Aeroplane('AAA111', 'Germany', 200, 10000)
    second = Aeroplane('BBB222', 'France', 250, 12000)

    assert first.compare_velocity(second) is False


def test_compare_velocity_equal():
    first = Aeroplane('AAA111', 'Germany', 250, 10000)
    second = Aeroplane('BBB222', 'France', 250, 12000)

    assert first.compare_velocity(second) is False


def test_compare_velocity_invalid_object(aeroplane):
    with pytest.raises(TypeError):
        aeroplane.compare_velocity('not an aeroplane')


# compare_baro_altitude


def test_compare_baro_altitude_first_is_higher():
    first = Aeroplane('AAA111', 'Germany', 250, 12000)
    second = Aeroplane('BBB222', 'France', 300, 10000)

    assert first.compare_baro_altitude(second) is True


def test_compare_baro_altitude_first_is_lower():
    first = Aeroplane('AAA111', 'Germany', 250, 8000)
    second = Aeroplane('BBB222', 'France', 300, 10000)

    assert first.compare_baro_altitude(second) is False


def test_compare_baro_altitude_equal():
    first = Aeroplane('AAA111', 'Germany', 250, 10000)
    second = Aeroplane('BBB222', 'France', 300, 10000)

    assert first.compare_baro_altitude(second) is False


def test_compare_baro_altitude_invalid_object(aeroplane):
    with pytest.raises(TypeError):
        aeroplane.compare_baro_altitude('not an aeroplane')


# to_dict


def test_to_dict(aeroplane):
    result = aeroplane.to_dict()

    assert result == {
        'callsign': 'AAA111',
        'origin_country': 'United States',
        'velocity': 250.5,
        'baro_altitude': 10000.0
    }
