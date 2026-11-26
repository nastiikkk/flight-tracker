from abc import ABC, abstractmethod
import json

from src.aeroplane import Aeroplane


class BaseSaver(ABC):

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def add_aeroplane(self, aeroplane):
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane):
        pass

    @abstractmethod
    def get_aeroplanes(self, criteria: dict):
        pass


class JSONSaver(BaseSaver):

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> list:

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

        except FileNotFoundError:
            return []

        except json.JSONDecodeError:
            return []

        return data

    def check_class_type(self, other: object) -> None:
        if not isinstance(other, Aeroplane):
            raise TypeError('Ожидается объект класса Aeroplane')

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        self.check_class_type(aeroplane)

        aeroplane_dict = aeroplane.to_dict()

        data = self.read()
        data.append(aeroplane_dict)
        
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:

        self.check_class_type(aeroplane)

        data = self.read()

        data = [
            item
            for item in data
            if item['callsign'] != aeroplane.callsign
        ]

        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_aeroplanes(self, criteria: dict) -> list:

        data = self.read()

        result = []

        for aeroplane in data:
            if all(
                aeroplane.get(key) == value
                for key, value in criteria.items()
            ):
                result.append(aeroplane)

        return result
