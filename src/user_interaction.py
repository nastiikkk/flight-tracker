from pathlib import Path

from requests.exceptions import RequestException

from src.api_classes import AeroplanesAPI
from src.aeroplane import Aeroplane
from src.storage import JSONSaver


DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'aeroplanes.json'


def filter_aeroplanes(
    aeroplanes: list[Aeroplane],
    filter_words: list[str]
) -> list[Aeroplane]:
    return [
        aeroplane
        for aeroplane in aeroplanes
        if aeroplane.origin_country in filter_words
    ]

def get_aeroplanes_by_altitude(
    aeroplanes: list[Aeroplane],
    altitude_range: str
) -> list[Aeroplane]:
    try:
        values = altitude_range.split('-')

        if len(values) != 2:
            raise ValueError

        min_altitude, max_altitude = map(float, values)

    except ValueError:
        raise ValueError(
            'Диапазон высот должен быть указан в формате: 1000-5000'
        )

    if min_altitude < 0 or max_altitude < 0:
        raise ValueError('Высота не может быть отрицательной')

    if min_altitude > max_altitude:
        raise ValueError(
            'Минимальная высота не может быть больше максимальной'
        )

    return [
        aeroplane
        for aeroplane in aeroplanes
        if min_altitude <= aeroplane.baro_altitude <= max_altitude
    ]


def sort_aeroplanes(
    aeroplanes: list[Aeroplane]
) -> list[Aeroplane]:
    return sorted(
        aeroplanes,
        key=lambda aeroplane: aeroplane.baro_altitude,
        reverse=True
    )


def get_top_aeroplanes(
    aeroplanes: list[Aeroplane],
    top_n: int
) -> list[Aeroplane]:
    if top_n <= 0:
        raise ValueError(
            'Количество самолётов должно быть больше нуля'
        )

    return aeroplanes[:top_n]


def print_aeroplanes(aeroplanes: list[Aeroplane]) -> None:

    if not aeroplanes:
        print('\nСамолёты не найдены')
        return

    print('\nНайденные самолёты:')

    for aeroplane in aeroplanes:
        print(
            f'\nБорт: {aeroplane.callsign}'
            f'\nСтрана происхождения: {aeroplane.origin_country}'
            f'\nСкорость: {aeroplane.velocity} м/с'
            f'\nВысота: {aeroplane.baro_altitude} м'
        )


def print_saved_aeroplanes(aeroplanes: list[dict]) -> None:

    if not aeroplanes:
        print('\nСамолёты не найдены')
        return

    print('\nСохранённые самолёты:')

    for aeroplane in aeroplanes:
        print(
            f'\nБорт: {aeroplane["callsign"]}'
            f'\nСтрана происхождения: {aeroplane["origin_country"]}'
            f'\nСкорость: {aeroplane["velocity"]} м/с'
            f'\nВысота: {aeroplane["baro_altitude"]} м'
        )


def save_aeroplanes(
    saver: JSONSaver,
    aeroplanes: list[Aeroplane]
) -> int:
    saved_data = saver.read()

    existing_callsigns = {
        item.get('callsign')
        for item in saved_data
        if isinstance(item, dict)
    }

    saved_count = 0

    for aeroplane in aeroplanes:
        if aeroplane.callsign not in existing_callsigns:
            saver.add_aeroplane(aeroplane)
            existing_callsigns.add(aeroplane.callsign)
            saved_count += 1

    return saved_count


def get_aeroplanes_from_api(
    api: AeroplanesAPI,
    saver: JSONSaver
) -> None:

    country = input(
        '\nВведите страну, над территорией которой искать самолёты: '
    ).strip()

    if not country:
        raise ValueError('Название страны не может быть пустым')

    data = api.get_aeroplanes(country)

    if not data:
        print('Страна не найдена')
        return

    aeroplanes = Aeroplane.cast_to_object_list(data)

    if not aeroplanes:
        print('Самолёты не найдены')
        return

    filter_input = input(
        '\nСамолёты каких стран происхождения оставить? '
        'Введите страны через запятую: '
    )

    filtered_aeroplanes = filter_aeroplanes(
        aeroplanes,
        filter_input.split(',')
    )

    altitude_range = input(
    '\nВведите диапазон высот, например 1000-10000: '
    )

    ranged_aeroplanes = get_aeroplanes_by_altitude(
        filtered_aeroplanes,
        altitude_range
    )

    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)

    top_n = int(
        input('\nСколько самолётов показать в топе по высоте? ')
    )

    top_aeroplanes = get_top_aeroplanes(
        sorted_aeroplanes,
        top_n
    )

    print('\nТоп самолётов по высоте:')
    print_aeroplanes(top_aeroplanes)

    if not sorted_aeroplanes:
        return

    save_choice = input(
        '\nСохранить найденные самолёты в JSON-файл?\n'
        '0 — Нет\n'
        '1 — Да\n'
        'Ваш выбор: '
    ).strip()

    if save_choice == '1':
        saved_count = save_aeroplanes(saver, top_aeroplanes)
        print(f'Добавлено новых самолётов: {saved_count}')

    elif save_choice == '0':
        print('Сохранение отменено')

    else:
        raise ValueError('Введите 0 или 1')


def delete_saved_aeroplane(saver: JSONSaver) -> None:

    callsign = input(
        '\nВведите callsign самолёта для удаления: '
    ).strip()

    if not callsign:
        raise ValueError('Callsign не может быть пустым')

    result = saver.get_aeroplanes({'callsign': callsign})

    if not result:
        print('Самолёт с таким callsign не найден')
        return

    aeroplane_data = result[0]

    aeroplane = Aeroplane(
        aeroplane_data['callsign'],
        aeroplane_data['origin_country'],
        aeroplane_data['velocity'],
        aeroplane_data['baro_altitude']
    )

    if saver.delete_aeroplane(aeroplane):
        print(f'Самолёт {callsign} удалён')


def search_saved_aeroplanes(saver: JSONSaver) -> None:

    print(
        '\nПоиск сохранённых самолётов:\n'
        '1 — По callsign\n'
        '2 — По стране происхождения\n'
        '3 — По скорости\n'
        '4 — По высоте'
    )

    choice = input('Ваш выбор: ').strip()

    criteria_fields = {
        '1': 'callsign',
        '2': 'origin_country',
        '3': 'velocity',
        '4': 'baro_altitude'
    }

    if choice not in criteria_fields:
        raise ValueError('Такого пункта поиска нет')

    field = criteria_fields[choice]

    value = input('Введите значение для поиска: ').strip()

    if not value:
        raise ValueError('Значение для поиска не может быть пустым')

    if field in ('velocity', 'baro_altitude'):
        try:
            value = float(value)
        except ValueError:
            raise ValueError(
                'Для поиска скорости и высоты нужно ввести число'
            )

    result = saver.get_aeroplanes({field: value})

    print_saved_aeroplanes(result)


def compare_saved_aeroplanes(saver: JSONSaver) -> None:

    first_callsign = input(
        '\nВведите callsign первого самолёта: '
    ).strip()

    second_callsign = input(
        'Введите callsign второго самолёта: '
    ).strip()

    if not first_callsign or not second_callsign:
        raise ValueError('Callsign не может быть пустым')

    first_result = saver.get_aeroplanes({'callsign': first_callsign})
    second_result = saver.get_aeroplanes({'callsign': second_callsign})

    if not first_result or not second_result:
        print('Один или оба самолёта не найдены')
        return

    first_data = first_result[0]
    second_data = second_result[0]

    first = Aeroplane(**first_data)
    second = Aeroplane(**second_data)

    if first.compare_velocity(second):
        print(f'{first.callsign} быстрее')
    elif second.compare_velocity(first):
        print(f'{second.callsign} быстрее')
    else:
        print('Скорость самолётов одинаковая')

    if first.compare_baro_altitude(second):
        print(f'{first.callsign} летит выше')
    elif second.compare_baro_altitude(first):
        print(f'{second.callsign} летит выше')
    else:
        print('Высота самолётов одинаковая')


def user_interaction() -> None:

    api = AeroplanesAPI()
    saver = JSONSaver(str(DATA_FILE))

    while True:

        print(
            '\n========== FLIGHT TRACKER ==========\n'
            '1 — Получить самолёты\n'
            '2 — Удалить сохранённый самолёт\n'
            '3 — Найти или сравнить сохранённые самолёты\n'
            '0 — Выход'
        )

        choice = input('Выберите действие: ').strip()

        try:
            if choice == '1':
                get_aeroplanes_from_api(api, saver)

            elif choice == '2':
                delete_saved_aeroplane(saver)

            elif choice == '3':
                print(
                    '\n1 — Поиск самолётов\n'
                    '2 — Сравнение двух самолётов'
                )

                search_choice = input('Ваш выбор: ').strip()

                if search_choice == '1':
                    search_saved_aeroplanes(saver)

                elif search_choice == '2':
                    compare_saved_aeroplanes(saver)

                else:
                    raise ValueError('Такого пункта нет')

            elif choice == '0':
                print('Работа программы завершена')
                break

            else:
                print('Такого пункта меню нет')

        except RequestException as error:
            print(f'Ошибка подключения к API: {error}')

        except (ValueError, TypeError, KeyError) as error:
            print(f'Ошибка: {error}')

        except OSError as error:
            print(f'Ошибка при работе с файлом: {error}')


if __name__ == '__main__':
    user_interaction()
