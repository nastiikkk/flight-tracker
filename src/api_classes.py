from abc import ABC, abstractmethod
from requests import get, HTTPError

class BaseAPI(ABC):

    @abstractmethod
    def get_aeroplanes(self, country: str):
        pass


class AeroplanesAPI(BaseAPI):
    def __init__(self) -> None:
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all?'
        self.aeroplanes = None

    def get_aeroplanes(self, country: str) -> dict:

        headers_nominatim = {
            'User-Agent': 'flight-tracker/1.0',
        }

        params_nominatim = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }

        response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)

        if response.status_code != 200:
            raise HTTPError()

        data = response.json()

        if not data:
            return {
                'time': None,
                'states': []
            }
        
        geo_coordinates = data[0].get('boundingbox')


        params = {
            'lamin': geo_coordinates[0],
            'lamax': geo_coordinates[1],
            'lomin': geo_coordinates[2],
            'lomax': geo_coordinates[3],
        }

        response = get(url=self.opensky_url, params=params)

        self.aeroplanes = response.json()

        return self.aeroplanes

api = AeroplanesAPI()
