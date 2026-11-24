class Aeroplane:

    def __init__(
            self, 
            callsign: str, 
            origin_country: str, 
            velocity: float, 
            baro_altitude: float
    ) -> None:
        if not isinstance(callsign, str):
            raise TypeError()

        if not isinstance(origin_country, str):
            raise TypeError()
        
        if not isinstance(velocity, (float, int)):
            raise TypeError()
        if velocity < 0:
            raise ValueError()

        if not isinstance(baro_altitude, (float, int)):
            raise TypeError()
        
        self.__callsign = callsign
        self.__origin_country = origin_country
        self.__velocity = velocity
        self.__baro_altitude = baro_altitude
        

    @classmethod
    def cast_to_object_list(cls, aeroplanes: dict) -> list:

        aeroplanes_list = []

        states = aeroplanes.get('states') or []

        for aeroplane in states:
            callsign = aeroplane[0]
            origin_country = aeroplane[2]
            baro_altitude = aeroplane[7]
            velocity = aeroplane[9]

            if None in (callsign, origin_country, baro_altitude, velocity):
                continue

            aeroplanes_list.append(
                cls(callsign, origin_country, velocity, baro_altitude)
            )

        return aeroplanes_list


    def check_class_type(self, other: object) -> None:
        if not isinstance(other, Aeroplane):
            raise TypeError('Ожидается объект класса Aeroplane')

    def compare_velocity(self, other: Aeroplane) -> bool:
        self.check_class_type(other)
        return self.velocity > other.velocity

    def compare_baro_altitude(self, other: Aeroplane) -> bool:
        self.check_class_type(other)
        return self.baro_altitude > other.baro_altitude
