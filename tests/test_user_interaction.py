
from unittest.mock import Mock, patch

import pytest

from src.aeroplane import Aeroplane
from src import user_interaction as ui


@pytest.fixture
def aeroplanes():
    return [
        Aeroplane('AAA111', 'United States', 250, 10000),
        Aeroplane('BBB222', 'Germany', 300, 12000),
        Aeroplane('CCC333', 'France', 200, 8000),
    ]


@pytest.fixture
def saver():
    return Mock()


# filter_aeroplanes


def test_filter_aeroplanes(aeroplanes):
    result = ui.filter_aeroplanes(
        aeroplanes,
        ['United States', 'France']
    )

    assert [plane.callsign for plane in result] == [
        'AAA111',
        'CCC333'
    ]


def test_filter_aeroplanes_no_matches(aeroplanes):
    result = ui.filter_aeroplanes(aeroplanes, ['Japan'])

    assert result == []


def test_filter_aeroplanes_empty_filter(aeroplanes):
    result = ui.filter_aeroplanes(aeroplanes, [])

    assert result == []


# get_aeroplanes_by_altitude


def test_get_aeroplanes_by_altitude(aeroplanes):
    result = ui.get_aeroplanes_by_altitude(
        aeroplanes,
        '9000-11000'
    )

    assert [plane.callsign for plane in result] == ['AAA111']


@pytest.mark.parametrize(
    'altitude_range',
    ['1000', '1000-2000-3000', 'abc-5000', '1000-abc', '']
)
def test_get_aeroplanes_by_altitude_invalid_format(
    aeroplanes,
    altitude_range
):
    with pytest.raises(ValueError):
        ui.get_aeroplanes_by_altitude(aeroplanes, altitude_range)


def test_get_aeroplanes_by_altitude_min_greater_than_max(aeroplanes):
    with pytest.raises(
        ValueError,
        match='Минимальная высота не может быть больше максимальной'
    ):
        ui.get_aeroplanes_by_altitude(aeroplanes, '10000-5000')


def test_get_aeroplanes_by_altitude_no_matches(aeroplanes):
    result = ui.get_aeroplanes_by_altitude(
        aeroplanes,
        '15000-20000'
    )

    assert result == []


# sort_aeroplanes


def test_sort_aeroplanes(aeroplanes):
    result = ui.sort_aeroplanes(aeroplanes)

    assert [plane.callsign for plane in result] == [
        'BBB222',
        'AAA111',
        'CCC333'
    ]


def test_sort_aeroplanes_does_not_change_original_list(aeroplanes):
    original = aeroplanes.copy()

    ui.sort_aeroplanes(aeroplanes)

    assert aeroplanes == original


# get_top_aeroplanes


def test_get_top_aeroplanes(aeroplanes):
    result = ui.get_top_aeroplanes(aeroplanes, 2)

    assert [plane.callsign for plane in result] == [
        'AAA111',
        'BBB222'
    ]


def test_get_top_aeroplanes_more_than_available(aeroplanes):
    result = ui.get_top_aeroplanes(aeroplanes, 10)

    assert result == aeroplanes


@pytest.mark.parametrize('top_n', [0, -1, -10])
def test_get_top_aeroplanes_invalid_number(aeroplanes, top_n):
    with pytest.raises(ValueError):
        ui.get_top_aeroplanes(aeroplanes, top_n)


# print_aeroplanes


def test_print_aeroplanes(aeroplanes, capsys):
    ui.print_aeroplanes(aeroplanes[:1])

    output = capsys.readouterr().out

    assert 'AAA111' in output
    assert 'United States' in output
    assert '250' in output
    assert '10000' in output


def test_print_aeroplanes_empty(capsys):
    ui.print_aeroplanes([])

    output = capsys.readouterr().out

    assert 'Самолёты не найдены' in output


# print_saved_aeroplanes


def test_print_saved_aeroplanes(capsys):
    saved_aeroplanes = [
        {
            'callsign': 'AAA111',
            'origin_country': 'United States',
            'velocity': 250,
            'baro_altitude': 10000
        }
    ]

    ui.print_saved_aeroplanes(saved_aeroplanes)

    output = capsys.readouterr().out

    assert 'AAA111' in output
    assert 'United States' in output
    assert '250' in output
    assert '10000' in output


def test_print_saved_aeroplanes_empty(capsys):
    ui.print_saved_aeroplanes([])

    output = capsys.readouterr().out

    assert 'Самолёты не найдены' in output


# save_aeroplanes


def test_save_aeroplanes(saver, aeroplanes):
    saver.read.return_value = []

    result = ui.save_aeroplanes(saver, aeroplanes)

    assert result == 3
    assert saver.add_aeroplane.call_count == 3


def test_save_aeroplanes_skips_existing(saver, aeroplanes):
    saver.read.return_value = [
        {'callsign': 'AAA111'}
    ]

    result = ui.save_aeroplanes(saver, aeroplanes)

    assert result == 2
    assert saver.add_aeroplane.call_count == 2


def test_save_aeroplanes_skips_duplicate_callsigns(saver, aeroplanes):
    saver.read.return_value = []

    result = ui.save_aeroplanes(
        saver,
        [aeroplanes[0], aeroplanes[0]]
    )

    assert result == 1
    saver.add_aeroplane.assert_called_once_with(aeroplanes[0])


def test_save_aeroplanes_empty_list(saver):
    saver.read.return_value = []

    result = ui.save_aeroplanes(saver, [])

    assert result == 0
    saver.add_aeroplane.assert_not_called()


# get_aeroplanes_from_api


def test_get_aeroplanes_from_api_saves_only_top(
    aeroplanes,
    saver
):
    api = Mock()
    api.get_aeroplanes.return_value = {'states': ['test']}

    with (
        patch('builtins.input', side_effect=[
            'Germany',
            'United States,Germany,France',
            '0-15000',
            '2',
            '1'
        ]),
        patch.object(
            Aeroplane,
            'cast_to_object_list',
            return_value=aeroplanes
        ),
        patch.object(ui, 'save_aeroplanes', return_value=2) as save_mock,
        patch.object(ui, 'print_aeroplanes') as print_mock
    ):
        ui.get_aeroplanes_from_api(api, saver)

    api.get_aeroplanes.assert_called_once_with('Germany')

    top_aeroplanes = [
        aeroplanes[1],
        aeroplanes[0]
    ]

    print_mock.assert_called_once_with(top_aeroplanes)
    save_mock.assert_called_once_with(saver, top_aeroplanes)


def test_get_aeroplanes_from_api_country_not_found(saver, capsys):
    api = Mock()
    api.get_aeroplanes.return_value = []

    with patch('builtins.input', return_value='Unknown'):
        ui.get_aeroplanes_from_api(api, saver)

    output = capsys.readouterr().out

    assert 'Страна не найдена' in output
    api.get_aeroplanes.assert_called_once_with('Unknown')


def test_get_aeroplanes_from_api_no_aeroplanes(saver, capsys):
    api = Mock()
    api.get_aeroplanes.return_value = {'states': []}

    with (
        patch('builtins.input', return_value='Germany'),
        patch.object(Aeroplane, 'cast_to_object_list', return_value=[])
    ):
        ui.get_aeroplanes_from_api(api, saver)

    output = capsys.readouterr().out

    assert 'Самолёты не найдены' in output


def test_get_aeroplanes_from_api_empty_country(saver):
    api = Mock()

    with patch('builtins.input', return_value='   '):
        with pytest.raises(ValueError, match='Название страны не может быть пустым'):
            ui.get_aeroplanes_from_api(api, saver)

    api.get_aeroplanes.assert_not_called()


def test_get_aeroplanes_from_api_cancel_save(aeroplanes, saver):
    api = Mock()
    api.get_aeroplanes.return_value = {'states': ['test']}

    with (
        patch('builtins.input', side_effect=[
            'Germany',
            'United States,Germany,France',
            '0-15000',
            '2',
            '0'
        ]),
        patch.object(
            Aeroplane,
            'cast_to_object_list',
            return_value=aeroplanes
        ),
        patch.object(ui, 'save_aeroplanes') as save_mock,
        patch.object(ui, 'print_aeroplanes')
    ):
        ui.get_aeroplanes_from_api(api, saver)

    save_mock.assert_not_called()


def test_get_aeroplanes_from_api_invalid_save_choice(aeroplanes, saver):
    api = Mock()
    api.get_aeroplanes.return_value = {'states': ['test']}

    with (
        patch('builtins.input', side_effect=[
            'Germany',
            'United States,Germany,France',
            '0-15000',
            '2',
            '5'
        ]),
        patch.object(
            Aeroplane,
            'cast_to_object_list',
            return_value=aeroplanes
        ),
        patch.object(ui, 'print_aeroplanes')
    ):
        with pytest.raises(ValueError, match='Введите 0 или 1'):
            ui.get_aeroplanes_from_api(api, saver)


# delete_saved_aeroplane


def test_delete_saved_aeroplane(saver, capsys):
    saver.get_aeroplanes.return_value = [
        {
            'callsign': 'AAA111',
            'origin_country': 'United States',
            'velocity': 250,
            'baro_altitude': 10000
        }
    ]
    saver.delete_aeroplane.return_value = True

    with patch('builtins.input', return_value='AAA111'):
        ui.delete_saved_aeroplane(saver)

    saver.get_aeroplanes.assert_called_once_with(
        {'callsign': 'AAA111'}
    )
    saver.delete_aeroplane.assert_called_once()

    output = capsys.readouterr().out
    assert 'Самолёт AAA111 удалён' in output


def test_delete_saved_aeroplane_not_found(saver, capsys):
    saver.get_aeroplanes.return_value = []

    with patch('builtins.input', return_value='AAA111'):
        ui.delete_saved_aeroplane(saver)

    saver.delete_aeroplane.assert_not_called()

    output = capsys.readouterr().out
    assert 'Самолёт с таким callsign не найден' in output


def test_delete_saved_aeroplane_empty_callsign(saver):
    with patch('builtins.input', return_value='   '):
        with pytest.raises(ValueError, match='Callsign не может быть пустым'):
            ui.delete_saved_aeroplane(saver)

    saver.get_aeroplanes.assert_not_called()


# search_saved_aeroplanes


@pytest.mark.parametrize(
    ('choice', 'value', 'expected'),
    [
        ('1', 'AAA111', {'callsign': 'AAA111'}),
        ('2', 'Germany', {'origin_country': 'Germany'}),
        ('3', '250', {'velocity': 250.0}),
        ('4', '10000', {'baro_altitude': 10000.0}),
    ]
)
def test_search_saved_aeroplanes(
    saver,
    choice,
    value,
    expected
):
    saver.get_aeroplanes.return_value = []

    with patch('builtins.input', side_effect=[choice, value]):
        ui.search_saved_aeroplanes(saver)

    saver.get_aeroplanes.assert_called_once_with(expected)


def test_search_saved_aeroplanes_invalid_choice(saver):
    with patch('builtins.input', return_value='5'):
        with pytest.raises(ValueError, match='Такого пункта поиска нет'):
            ui.search_saved_aeroplanes(saver)

    saver.get_aeroplanes.assert_not_called()


def test_search_saved_aeroplanes_empty_value(saver):
    with patch('builtins.input', side_effect=['1', '   ']):
        with pytest.raises(
            ValueError,
            match='Значение для поиска не может быть пустым'
        ):
            ui.search_saved_aeroplanes(saver)

    saver.get_aeroplanes.assert_not_called()


def test_search_saved_aeroplanes_invalid_number(saver):
    with patch('builtins.input', side_effect=['3', 'fast']):
        with pytest.raises(
            ValueError,
            match='Для поиска скорости и высоты нужно ввести число'
        ):
            ui.search_saved_aeroplanes(saver)

    saver.get_aeroplanes.assert_not_called()


# compare_saved_aeroplanes


def test_compare_saved_aeroplanes(saver, capsys):
    saver.get_aeroplanes.side_effect = [
        [
            {
                'callsign': 'AAA111',
                'origin_country': 'United States',
                'velocity': 300,
                'baro_altitude': 12000
            }
        ],
        [
            {
                'callsign': 'BBB222',
                'origin_country': 'Germany',
                'velocity': 250,
                'baro_altitude': 10000
            }
        ]
    ]

    with patch('builtins.input', side_effect=['AAA111', 'BBB222']):
        ui.compare_saved_aeroplanes(saver)

    output = capsys.readouterr().out

    assert 'AAA111 быстрее' in output
    assert 'AAA111 летит выше' in output


def test_compare_saved_aeroplanes_same_values(saver, capsys):
    aeroplane_data = {
        'callsign': 'AAA111',
        'origin_country': 'United States',
        'velocity': 250,
        'baro_altitude': 10000
    }

    saver.get_aeroplanes.side_effect = [
        [aeroplane_data],
        [{
            **aeroplane_data,
            'callsign': 'BBB222'
        }]
    ]

    with patch('builtins.input', side_effect=['AAA111', 'BBB222']):
        ui.compare_saved_aeroplanes(saver)

    output = capsys.readouterr().out

    assert 'Скорость самолётов одинаковая' in output
    assert 'Высота самолётов одинаковая' in output


def test_compare_saved_aeroplanes_not_found(saver, capsys):
    saver.get_aeroplanes.side_effect = [[], []]

    with patch('builtins.input', side_effect=['AAA111', 'BBB222']):
        ui.compare_saved_aeroplanes(saver)

    output = capsys.readouterr().out

    assert 'Один или оба самолёта не найдены' in output


def test_compare_saved_aeroplanes_empty_callsign(saver):
    with patch('builtins.input', side_effect=['', 'BBB222']):
        with pytest.raises(ValueError, match='Callsign не может быть пустым'):
            ui.compare_saved_aeroplanes(saver)

    saver.get_aeroplanes.assert_not_called()


# user_interaction


def test_user_interaction_exit():
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch('builtins.input', return_value='0'),
    ):
        ui.user_interaction()


def test_user_interaction_invalid_menu_choice(capsys):
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch('builtins.input', side_effect=['5', '0']),
    ):
        ui.user_interaction()

    output = capsys.readouterr().out

    assert 'Такого пункта меню нет' in output


def test_user_interaction_api_request_error(capsys):
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch.object(
            ui,
            'get_aeroplanes_from_api',
            side_effect=ui.RequestException('Connection error')
        ),
        patch('builtins.input', side_effect=['1', '0'])
    ):
        ui.user_interaction()

    output = capsys.readouterr().out

    assert 'Ошибка подключения к API' in output
    assert 'Connection error' in output


def test_user_interaction_value_error(capsys):
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch.object(
            ui,
            'get_aeroplanes_from_api',
            side_effect=ValueError('Некорректное значение')
        ),
        patch('builtins.input', side_effect=['1', '0'])
    ):
        ui.user_interaction()

    output = capsys.readouterr().out

    assert 'Ошибка: Некорректное значение' in output


def test_user_interaction_delete_saved_aeroplane():
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch.object(ui, 'delete_saved_aeroplane') as delete_mock,
        patch('builtins.input', side_effect=['2', '0'])
    ):
        ui.user_interaction()

    delete_mock.assert_called_once()


def test_user_interaction_search_saved_aeroplanes():
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch.object(ui, 'search_saved_aeroplanes') as search_mock,
        patch('builtins.input', side_effect=['3', '1', '0'])
    ):
        ui.user_interaction()

    search_mock.assert_called_once()


def test_user_interaction_compare_saved_aeroplanes():
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch.object(ui, 'compare_saved_aeroplanes') as compare_mock,
        patch('builtins.input', side_effect=['3', '2', '0'])
    ):
        ui.user_interaction()

    compare_mock.assert_called_once()


def test_user_interaction_invalid_search_submenu(capsys):
    with (
        patch.object(ui, 'AeroplanesAPI'),
        patch.object(ui, 'JSONSaver'),
        patch('builtins.input', side_effect=['3', '5', '0'])
    ):
        ui.user_interaction()

    output = capsys.readouterr().out

    assert 'Ошибка: Такого пункта нет' in output
