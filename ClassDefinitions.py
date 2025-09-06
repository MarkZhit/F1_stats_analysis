from typing import List
import numpy as np
from numpy.typing import NDArray
import requests
from bs4 import BeautifulSoup

class Driver:
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
        super().__init__(driver, constructor, time)
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

    def get_table_from_wiki_following_div(url: str, prev_div_id: str) -> NDArray:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        # print(url)
        session = requests.Session()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the div containing the text prev_div
        # try:
        if ("Indianapolis" in url):
            prev_div_id = "Box_score"

        div = soup.find(id=prev_div_id)
        # print("prev div id: ", prev_div_id, ", div: ", div)
        try:
            table = div.parent.find_next_sibling("table")  # get the table after that div
        except Exception as e:
            # TODO: still getting ragged table
            print("getting table (quali) got an exception: ", e, "url: ", url)
            raise e
        # table = div.find_next("table")
        # except Exception as e:
        #     print("Got error: ", e)
        #     raise e

        all_rows = table.tbody.find_all("tr")

        rows = [r for r in all_rows if r.td]

        # extract text for each cell
        dataTable = []
        for i, row in enumerate(rows):
            if (row.get("class") and "sortbottom" in row.get("class")):
                continue

            dataRow = []
            cells = row.find_all("td")

            # print(len(cells))
            maxWidth = 0

            headerRow = table.thead.find_all("tr")[0].find_all("th")
            for i,th in enumerate(headerRow):
                if th.has_attr("colspan"):
                    maxWidth += int(th["colspan"])
                else:
                    maxWidth += 1


            if (len(cells) < maxWidth):
                # if row is short
                currCells = cells
                cells = rows[i - 1].find_all("td")
                # find the previous row
                for j, cell in enumerate(cells):
                    if cell.has_attr("rowspan"):
                        # find every element with rowspan
                        rowspan = int(cell["rowspan"])
                        newCell = cell
                        newCell["rowspan"] = rowspan - 1
                        currCells.insert(j,newCell)
                        cells = currCells


                # cells[1] = currCells[0]

                # TODO: maybe generaly to look at prev, and for any element where rowspan!=2,
                # then you copy it over to the current one

            # print("Row is >= 16 cells")
            for j, cell in enumerate(cells):
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
                print("prev row was longer (quali) j= ", j, "url: ", url)

            # print(len(dataRow))

            # TODO: instead of saving as NDArray, save directly to the type I need?
            # that way I avoid problems of adding useless columns of null
            # this woudl require refactoring, and creating different versions of this function
            # that convert to the right type

            # dataRow.append([cell])
            # if (len(dataRow) > 0):
            dataTable.append(dataRow)

        returnVal = np.array(dataTable)
        return returnVal

    def get_quali_from_link(url: str):
        # TODO get the whole table, each row becomes one QualiPosition
        qualiTable: NDArray = Quali.get_table_from_wiki_following_div(url, "Qualifying")
        # print(qualiTable)
        # TODO properly create instances of QualiPosition from the row
        qualiList: List[QualiPosition] = []
        for row in qualiTable:
            qualiPosition = QualiPosition(Driver("driver"), Constructor("constructor"), "time", 0)
            qualiList.append(qualiPosition)
        return Quali(qualiList)
        # return ClassDefinitions.Quali([]) # stub


class Results:
    def __init__(self, position: List[RacePosition]):
        self.position = position

    positions: List[RacePosition]

    def get_table_from_wiki_following_div(url: str, prev_div_id: str) -> NDArray:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        # print(url)
        session = requests.Session()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the div containing the text prev_div
        # try:
        if ("Indianapolis" in url):
            prev_div_id = "Box_score"

        div = soup.find(id=prev_div_id)
        # print("prev div id: ", prev_div_id, ", div: ", div)
        try:
            table = div.parent.find_next_sibling("table")  # get the table after that div
        except Exception as e:
            print("getting table (Restults) got an exception: ", e, "url: ", url)
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

            # print(len(cells))
            if (len(cells) < 7):
                currCells = cells
                cells = rows[i - 1].find_all("td")
                cells[1] = currCells[0]

            for j, cell in enumerate(cells):
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
                print("prev row was longer (results) j= ", j, "url: ", url)

            # print(len(dataRow))

            # TODO: instead of saving as NDArray, save directly to the type I need?
            # that way I avoid problems of adding useless columns of null
            # this woudl require refactoring, and creating different versions of this function
            # that convert to the right type

            # dataRow.append([cell])
            # if (len(dataRow) > 0):
            dataTable.append(dataRow)
        # print(len(dataTable))

        # TODO: somehow getting different length rows
        # print(len(dataRow))

        # Stub to get only one row
        # return dataTable
        returnVal = np.array(dataTable)
        return returnVal

    def get_results_from_link(url: str):
        # TODO get the whole table, each row becomes one RacePosition
        raceTable: NDArray = Results.get_table_from_wiki_following_div(url, "Race")
        # print(raceTable)
        # TODO properly create instances of RacePosition from the row
        raceList: List[RacePosition] = []
        for row in raceTable:
            racePosition = RacePosition(Driver("driver"), Constructor("constructor"), 0, "time", 0)
            raceList.append(racePosition)
        return Results(raceList)

class Race:
    def __init__(self, url: str, circuit: str, date, quali:Quali, results:Results):
        self.url = url
        self.circuit = circuit
        self.date = date
        self.quali = quali
        self.results = results

    url: str
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        # print(url)
        session = requests.Session()
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the div containing the text prev_div
        # try:
        if ("Indianapolis" in url):
            prev_div_id = "Box_score"

        div = soup.find(id=prev_div_id)
        # print("prev div id: ", prev_div_id, ", div: ", div)
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

            # print(len(cells))
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

            # print(len(dataRow))

            # TODO: instead of saving as NDArray, save directly to the type I need?
            # that way I avoid problems of adding useless columns of null
            # this woudl require refactoring, and creating different versions of this function
            # that convert to the right type

            # dataRow.append([cell])
            # if (len(dataRow) > 0):
            dataTable.append(dataRow)
        # print(len(dataTable))

        # TODO: somehow getting different length rows
        # print(len(dataRow))

        # Stub to get only one row
        # return dataTable
        returnVal = np.array(dataTable)
        return returnVal

    def get_race_from_link(url: str):
        return Race(url, "circuit", "date",
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
