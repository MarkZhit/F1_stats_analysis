import copy
from typing import List
import numpy as np
from numpy.typing import NDArray
import requests
from bs4 import BeautifulSoup

WIKIHEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

class NamedEntity:
    _instances = {}
    name: str
    url: str

    def __new__(cls, name: str, url: str):
        if name in cls._instances:
            return cls._instances[name]
        instance = super().__new__(cls)
        cls._instances[name] = instance
        return instance

    def __init__(self, name: str, url: str):
        # ensure we don’t overwrite existing state if reused
        if not hasattr(self, "_initialized"):
            self.name = name
            self.url = url
            self._initialized = True

    def __repr__(self) -> str:
        pass

class Driver(NamedEntity):
    def __repr__(self):
        return f"<Driver {self.name}>"

class Constructor(NamedEntity):
    def __repr__(self):
        return f"<Constructor {self.name}>"


class Position:
    def __init__(self, driver: Driver, constructor: Constructor, time: str):
        self.driver = driver
        self.constructor = constructor
        self.time = time

    driver:Driver
    constructor:Constructor
    time:str

class QualiPosition(Position):
    def __init__(self, driver: Driver, constructor: Constructor, grid_position: int, times: List[str]):
        super().__init__(driver, constructor, max(times))
        # max prolly doesn't work on strings, prolly need to define another method for this
        self.grid_position = grid_position

    grid_position: int

class RacePosition(Position):
    def __init__(self, driver:Driver, constructor: Constructor, laps: int, time: str, points: int):
        super().__init__(driver, constructor, time)
        self.laps = laps
        self.points = points

    laps: int
    points: int


class Quali:
    def __init__(self, positions: List[QualiPosition]):
        self.positions = positions

    positions: List[QualiPosition]

    def get_table_from_wiki_following_div(url: str) -> List[QualiPosition]:

        # print(url)
        session = requests.Session()
        resp = requests.get(url, headers=WIKIHEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the div containing the text prev_div
        prev_div_id = "Qualifying"
        if "1953_French" in url:
            prev_div_id = "Qualifying_classification"
        elif "1950_Indianapolis" in url:
            prev_div_id = prev_div_id
        elif "1957_Indianapolis" in url:
            prev_div_id = "Grid"
        elif ("Indianapolis" in url):
            prev_div_id = "Starting_grid"

        div = soup.find(id=prev_div_id)
        # print("prev div id: ", prev_div_id, ", div: ", div)
        try:
            table = div.parent.find_next_sibling("table")  # get the table after that div
        except Exception as e:
            print("Table doesn't exist after div, e: ", e, "url: ", url)
            raise e

        rows = table.tbody.find_all("tr")

        maxWidth, headerHeight = getHeaderDimensions(rows)

        # remove the header and footer
        rows = rows[headerHeight:-1]

        # extract relevant text from each cell
        qualiList: List[QualiPosition] = []
        for i, row in enumerate(rows):
            # row = [cell for cell in row if cell.name is not None]
            # if (row.get("class") and "sortbottom" in row.get("class")):
            #     continue

            cells = row.find_all("td")

            if (len(cells) > maxWidth):
                print("more cells than useful columns, len(cells): ", len(cells), "maxWidth: ", maxWidth)
                cells = cells[:maxWidth]

            # print(len(cells))



            if (len(cells) < maxWidth):
                # if row is short
                cells = copy.deepcopy(cells)
                prevCells = rows[i - 1].find_all("td")
                # find the previous row
                newRow = copy.deepcopy(row)
                for j, cell in enumerate(prevCells):
                    if cell.has_attr("rowspan"):
                        # find every element with rowspan
                        rowspan = int(cell["rowspan"])
                        newCell = copy.deepcopy(cell)
                        newCell["rowspan"] = rowspan - 1
                        cells.insert(j,newCell)
                        newRow.insert(2*j+2,'\n')
                        newRow.insert(2*j+3,newCell)
                # cells = copy.deepcopy(cells) # necessary?
                rows[i] = newRow

            # print("Row is >= 16 cells")
            racerName = ""
            racerURL = ""
            constructorName = ""
            constructorURL = ""
            gridPosition = i + 1
            times = []
            for j, cell in enumerate(cells):
                # Try direct child <a> first
                match j:
                    case 0:
                        continue
                    case 1:
                        # racer name
                        racerName = cell.find_all("a")[-1].get_text()
                        racerURL = "https://en.wikipedia.org" + cell.find_all("a")[-1]["href"]
                    case 2:
                        # constructor name
                        constructorName = cell.find_all("a")[-1].get_text()
                        constructorURL = "https://en.wikipedia.org" + cell.find_all("a")[-1]["href"]
                    case _:
                        # else, record for fun
                        times.append(cell.text)
            qualiList.append(QualiPosition(Driver(racerName, racerURL), Constructor(constructorName, constructorURL), gridPosition, times))

        print("QualiList   created for url:", url)
        # # print(returnVal)
        # return returnVal
        return Quali(qualiList)

    def get_quali_from_link(url: str):
        return Quali(Quali.get_table_from_wiki_following_div(url))
        # return ClassDefinitions.Quali([]) # stub


class Results:
    def __init__(self, position: List[RacePosition]):
        self.position = position

    positions: List[RacePosition]

    def get_table_from_wiki_following_div(url: str) -> List[RacePosition]:

        session = requests.Session()
        resp = requests.get(url, headers=WIKIHEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the div containing the text prev_div
        prev_div_id = "Race"
        if ("1953_French" in url):
            prev_div_id = "Race_classification"
        elif ("Indianapolis" in url):
            prev_div_id = "Box_score"

        div = soup.find(id=prev_div_id)
        # print("prev div id: ", prev_div_id, ", div: ", div)
        try:
            table = div.parent.find_next_sibling("table")  # get the table after that div
        except Exception as e:
            print("Table doesn't exist after div, e: ", e, "url: ", url)
            raise e

        rows = table.tbody.find_all("tr")

        maxWidth, headerHeight = getHeaderDimensions(rows)

        # remove the header and footer
        header = rows[0:headerHeight]
        gridIndex = getGridFromHeader(header)
        driverIndex = getDriverFromHeader(header)
        constructorIndex = getConstructorFromHeader(header)
        lapsIndex = getLapsFromHeader(header)
        timeIndex = getTimeFromHeader(header)
        pointsIndex = getPointsFromHeader(header)
        rows = rows[headerHeight:-1]

        # extract relevant text from each cell
        resultsList: List[RacePosition] = []
        for i, row in enumerate(rows):
            cells = row.find_all("td")

            if (len(cells) > maxWidth):
                print("more cells than useful columns, len(cells): ", len(cells), "maxWidth: ", maxWidth)
                cells = cells[:maxWidth]


            if (len(cells) < maxWidth):
                # if row is short
                cells = copy.deepcopy(cells)
                prevCells = rows[i - 1].find_all("td")
                # find the previous row
                newRow = copy.deepcopy(row)
                for j, cell in enumerate(prevCells):
                    if cell.has_attr("rowspan"):
                        # find every element with rowspan
                        rowspan = int(cell["rowspan"])
                        newCell = copy.deepcopy(cell)
                        newCell["rowspan"] = rowspan - 1
                        cells.insert(j,newCell)
                        newRow.insert(2*j+2,'\n')
                        newRow.insert(2*j+3,newCell)
                # cells = copy.deepcopy(cells) # necessary?
                rows[i] = newRow

            laps = 0
            time = ""
            points = 0
            racerName = ""
            racerURL = ""
            constructorName = ""
            constructorURL = ""
            for j, cell in enumerate(cells):
                # Try direct child <a> first
                # these indices differ for different websites
                if (j == driverIndex):
                    # racer name
                    racerName = cell.find_all("a")[-1].get_text()
                    racerURL = "https://en.wikipedia.org" + cell.find_all("a")[-1]["href"]
                elif (j == constructorIndex):
                    # constructor name
                    constructorName = cell.find_all("a")[-1].get_text()
                    constructorURL = "https://en.wikipedia.org" + cell.find_all("a")[-1]["href"]
                elif (j == lapsIndex):
                    laps = cell.text
                elif (j == timeIndex):
                    time = cell.text
                elif (j == pointsIndex):
                    if len(cell.find_all("b")) > 0:
                        points = cell.find_all("b")[0].get_text()
                    else:
                        points = 0

            resultsList.append(RacePosition(Driver(racerName, racerURL), Constructor(constructorName, constructorURL), laps, time, points))

        print("ResultsList created for url:", url)
        # # print(returnVal)
        # return returnVal
        return Results(resultsList)

    def get_results_from_link(url: str):
        return Results(Results.get_table_from_wiki_following_div(url))

class Race:
    def __init__(self, url: str, year: int, circuit: str, date, quali:Quali, results:Results):
        self.url = url
        self.year = year
        self.circuit = circuit
        self.date = date
        self.quali = quali
        self.results = results

    url: str
    year: int
    circuit: str
    date: str
    quali: Quali
    results: Results

class Season:
    def __init__(self, url: str, races: List[Race]):
        self.url = url
        self.races = races

    url: str
    races: List[Race]



    def get_table_from_wiki_following_div(url: str, prev_div_id: str) -> NDArray:
        session = requests.Session()
        resp = requests.get(url, headers=WIKIHEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        div = soup.find(id=prev_div_id)
        try:
            table = div.parent.find_next_sibling("table")  # get the table after that div
        except Exception as e:
            print("getting table (Season) got an exception: ", e, "url: ", url)
            raise e

        all_rows = table.tbody.find_all("tr")

        rows = [r for r in all_rows if r.td]

        # extract text for each cell
        dataTable = []
        for i, row in enumerate(rows):
            if (row.get("class") and "sortbottom" in row.get("class")):
                continue

            dataRow = []
            cells = row.find_all("td")

            if (len(cells) < 6):
                currCells = cells
                cells = rows[i - 1].find_all("td")
                cells[1] = currCells[0]

            # print("Row is >= 16 cells")
            for j,cell in enumerate(cells):
                # Try direct child <a> first
                a_tag = cell.find("a", recursive=False)  # td > a
                if a_tag is None:
                    # fallback: look for <a> inside a span
                    span = cell.find("span")
                    if span:
                        a_tag = span.find("a")

                if a_tag:
                    text = a_tag.get_text(strip=True)
                    href = a_tag.get("href")
                else:
                    text = cell.get_text(strip=True)
                    href = None

                dataRow.append([text, href])
            if (len(dataTable) and len(dataRow) < len(dataTable[-1])):
                print("prev row was longer (season) j= ", j, "url: ", url)

            dataTable.append(dataRow)
        returnVal = np.array(dataTable)
        return returnVal

    def get_race_from_link(url: str):
        return Race(url,0,  "circuit", "date",
                    Quali.get_quali_from_link(url), Results.get_results_from_link(url))

    def get_races_from_links(urls: List[str]):
        races: List[Race] = []
        for url in urls:
            races.append(Season.get_race_from_link(url))

        return races



    def get_F1_season(url: str, prev_div_id:str):
        season_table:NDArray = Season.get_table_from_wiki_following_div(url, prev_div_id)
        # season_race_links = season_table[:, -1, 1]
        season_race_links = [row[-1][1] for row in season_table]
        season_races = np.char.add("https://en.wikipedia.org", season_race_links)
        return Season(url, Season.get_races_from_links(season_races))


def getGridFromHeader(header) ->int:
    return getIndexFromHeader(header, "Grid")
def getDriverFromHeader(header) ->int:
    return getIndexFromHeader(header, "Driver")
def getConstructorFromHeader(header) ->int:
    return getIndexFromHeader(header, "Constructor")
def getLapsFromHeader(header) ->int:
    return getIndexFromHeader(header, "Laps")
def getTimeFromHeader(header) ->int:
    return getIndexFromHeader(header, "Time")
def getPointsFromHeader(header) ->int:
    return getIndexFromHeader(header, "Points")

def getIndexFromHeader(header, str):
    if (len(header) == 1):
        # simple, just go through, and get the one with the same text
        for i, col, in enumerate(header):
            if col.text == str:
                return i
    else:
        # len header > 1
        # relevant stuff is prolly in the first row anyways, just go through that
        for i, col, in enumerate(header):
            if col.text == str:
                return i


def getHeaderDimensions(rows) -> {int, int}:
    maxWidth = -1
    headerHeight = 1
    headerRow = rows[0]
    header_cells = [cell for cell in headerRow if cell.name is not None]
    for i, th in enumerate(header_cells):
        if ("Gap" in th.name):
            continue
        if th.has_attr("colspan"):
            maxWidth += int(th["colspan"])
        else:
            maxWidth += 1
        if th.has_attr("rowspan"):
            headerHeight = max(int(th["rowspan"]), headerHeight)
    return {headerHeight, maxWidth}