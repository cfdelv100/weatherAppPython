from dataclasses import dataclass


@dataclass(frozen=True)
class AirportRecord:
    code: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    airlines: list[dict]


class AirportService:
    def __init__(self):
        self._airports = {
            "LAX": AirportRecord(
                code="LAX",
                name="Los Angeles International Airport",
                city="Los Angeles",
                country="United States",
                latitude=33.9416,
                longitude=-118.4085,
                airlines=[
                    {"name": "American Airlines", "iata": "AA", "terminal": "4,5"},
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "2,3"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "7,8"},
                ],
            ),
            "JFK": AirportRecord(
                code="JFK",
                name="John F. Kennedy International Airport",
                city="New York",
                country="United States",
                latitude=40.6413,
                longitude=-73.7781,
                airlines=[
                    {"name": "American Airlines", "iata": "AA", "terminal": "8"},
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "2,4"},
                    {"name": "JetBlue Airways", "iata": "B6", "terminal": "5"},
                ],
            ),
            "ORD": AirportRecord(
                code="ORD",
                name="O'Hare International Airport",
                city="Chicago",
                country="United States",
                latitude=41.9742,
                longitude=-87.9073,
                airlines=[
                    {"name": "American Airlines", "iata": "AA", "terminal": "3"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "1"},
                    {"name": "Air Canada", "iata": "AC", "terminal": "5"},
                ],
            ),
            "ATL": AirportRecord(
                code="ATL",
                name="Hartsfield-Jackson Atlanta International Airport",
                city="Atlanta",
                country="United States",
                latitude=33.6407,
                longitude=-84.4277,
                airlines=[
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "S,N"},
                    {"name": "Southwest Airlines", "iata": "WN", "terminal": "N"},
                    {"name": "Spirit Airlines", "iata": "NK", "terminal": "N"},
                ],
            ),
            "DFW": AirportRecord(
                code="DFW",
                name="Dallas/Fort Worth International Airport",
                city="Dallas",
                country="United States",
                latitude=32.8998,
                longitude=-97.0403,
                airlines=[
                    {"name": "American Airlines", "iata": "AA", "terminal": "A,B,C,D"},
                    {"name": "Delta Air Lines", "iata": "DL", "terminal": "E"},
                    {"name": "United Airlines", "iata": "UA", "terminal": "E"},
                ],
            ),
        }

        self._city_map = {
            "los angeles": "LAX",
            "new york": "JFK",
            "chicago": "ORD",
            "atlanta": "ATL",
            "dallas": "DFW",
        }

    def get_airport_by_code(self, airport_code: str) -> dict | None:
        record = self._airports.get(airport_code.upper())
        return None if record is None else record.__dict__

    def get_airport_by_city(self, city: str) -> dict | None:
        airport_code = self._city_map.get(city.strip().lower())
        if not airport_code:
            return None
        return self.get_airport_by_code(airport_code)
