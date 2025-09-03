from lib2to3.pgen2.driver import Driver
from typing import List

class Racer:
    def __init__(self, name: str):
        self.name = name

    name: str

class Constructor:
    def __init__(self, name: str):
        self.name = name

    name: str

class Position:
    def __init__(self, driver: Driver, constructor: Constructor, time: str):
        self.driver = driver
        self.constructor = constructor
        self.time = time

    driver:Driver
    constructor:Constructor
    time:str

class QualiPosition(Position):
    def __init__(self, driver: Driver, constructor: Constructor, time: str, grid_position: int):
        super().__init__(self, driver, constructor, time)
        self.grid_position = grid_position

    grid_position: int

class RacePosition:
    def __init__(self, driver:Driver, constructor: Constructor, laps: int, time: str, points: int):
        super().__init__(self, driver, constructor, time)
        self.laps = laps
        self.points = points

    laps: int
    points: int


class Quali:
    def __init__(self, positions: List[QualiPosition]):
        self.positions = positions

    positions: List[QualiPosition]


class Results:
    def __init__(self, position: List[RacePosition]):
        self.position = position

    positions: List[RacePosition]

class Race:
    def __init__(self, url: str, circuit: str, date, quali:Quali, results:Results):
        self.url = url
        self.circuit = circuit
        self.date = date

    url: str
    circuit: str
    date: str
    quali: Quali
    results: Results

class Season:
    def __init__(self, name: str, races: List[Race]):
        self.name = name
        self.races = races

    year: int
    races: List[Race]