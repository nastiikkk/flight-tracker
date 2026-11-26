# Flight Tracker

Консольное приложение для получения и анализа информации о самолётах с помощью OpenSky Network API и OpenStreetMap (Nominatim).

## Возможности

- Получение списка самолётов по стране.
- Фильтрация по стране и высоте.
- Сортировка по высоте и выбор топ-N самолётов.
- Сравнение скорости и высоты самолётов.
- Сохранение, поиск и удаление самолётов в JSON-файле.

## Технологии

- Python
- Requests
- Pytest
- Poetry
- JSON

## Установка

```bash
git clone https://github.com/nastiikkk/flight-tracker/
cd <flight-tracker>
poetry install
```

## Запуск

```bash
poetry run python main.py
```

## Тестирование

```bash
poetry run pytest
```
