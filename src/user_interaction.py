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
        print('Самолёты не найдены')
        return

    print('\nНайденные самолёты:')

    for aeroplane in aeroplanes:
        print(
            f'Борт: {aeroplane.callsign}, '
            f'Страна происхождения: {aeroplane.origin_country}, '
            f'Скорость: {aeroplane.velocity} м/с, '
            f'Высота: {aeroplane.baro_altitude} м'
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


def user_interaction() -> None:
    api = AeroplanesAPI()
    saver = JSONSaver(str(DATA_FILE))

    try:
        country = input('Введите название страны для поиска самолётов: ').strip()

        if not country:
            raise ValueError('Название страны не может быть пустым')

        data = api.get_aeroplanes(country)

        if not data:
            print('По указанной стране самолёты не найдены')
            return

        aeroplanes = Aeroplane.cast_to_object_list(data)

        if not aeroplanes:
            print('Самолёты не найдены')
            return

        top_n = int(
            input(
                'Введите количество самолётов для вывода в топ N: '
            )
        )

        filter_input = input(
            'Самолёты каких стран происхождения оставить? '
            'Введите страны через запятую: '
        )

        filter_words = filter_input.split(',')

        altitude_range = input(
            'Введите диапазон высот полёта, например 1000-5000: '
        )

        filtered_aeroplanes = filter_aeroplanes(
            aeroplanes,
            filter_words
        )

        ranged_aeroplanes = get_aeroplanes_by_altitude(
            filtered_aeroplanes,
            altitude_range
        )

        sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)

        top_aeroplanes = get_top_aeroplanes(
            sorted_aeroplanes,
            top_n
        )

        print_aeroplanes(top_aeroplanes)

        save_choice = input(
            '\nСохранить отфильтрованные самолёты в JSON-файл?\n'
            '0 — Нет\n'
            '1 — Да\n'
            'Ваш выбор: '
        )

        if save_choice == '1':
            saved_count = save_aeroplanes(saver, ranged_aeroplanes)
            print(f'В JSON добавлено новых самолётов: {saved_count}')

        elif save_choice == '0':
            print('Сохранение отменено')

        else:
            raise ValueError('Введите 0 или 1')

    except RequestException as error:
        print(f'Ошибка при обращении к API: {error}')

    except ValueError as error:
        print(f'Ошибка ввода или данных: {error}')

    except OSError as error:
        print(f'Ошибка при работе с JSON-файлом: {error}')


if __name__ == '__main__':
    user_interaction()