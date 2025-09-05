""" Sources """
import os

# https://medium.com/pipeline-a-data-engineering-resource/how-i-used-python-to-scrape-100-tables-containing-5-years-of-f1-data-2e64125903c8
# ^ explains concept for webscraping

# https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions
# ^ contains a table with the list of f1 seasons by year (with wiki links)
# https://en.wikipedia.org/wiki/2000_Formula_One_World_Championship
# ^ year, contains a table with list of people and races (with wiki links)
# https://en.wikipedia.org/wiki/2000_Australian_Grand_Prix
# ^ individual race, contains quali and race results in two separate tables


""" imports """
from typing import List
from bs4 import BeautifulSoup
import numpy as np
from numpy.typing import NDArray
import json
import requests
import ClassDefinitions
from ClassDefinitions import Season

""" Function definitions """

def get_table_from_wiki_captioned(url: str, table_caption: str) -> NDArray:
    headers = {"User-Agent": "Mozilla/5.0"}  # looks like a browser
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for table in soup.find_all("table", {"class": "wikitable"}):
        caption = table.caption.get_text()
        if not (caption and (table_caption in table.caption.get_text())):
            continue

        all_rows = table.tbody.find_all("tr")
        rows = [r for r in all_rows if r.find("td")]

        # extract text for each cell
        dataTable = []
        for row in rows:
            dataRow = []
            cells = row.find_all("td")
            if (len(cells) < 16):
                print("Row is < 16 cells")
                # print("url: " + url)
                print("row: ")
                print(row)
                continue
            # print("Row is >= 16 cells")
            for cell in cells:
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


                # dataRow.append([cell])
            if (len(dataRow) > 0):
                dataTable.append(dataRow)
                # print(len(dataRow))

                # Stub to get only one row
                # return dataTable

        # convert to NumPy array
        # table_body = np.array(data)
        return np.array(dataTable)

    raise ValueError(f"No table found with caption '{table_caption}'")


def get_table_from_wiki_following_div(url: str, prev_div_id: str, table_width=6) -> NDArray:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    print(url)
    session = requests.Session()
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find the div containing the text prev_div
    # try:
    div = soup.find(id=prev_div_id)
    # print("prev div id: ", prev_div_id, ", div: ", div)
    table = div.parent.find_next_sibling("table")  # get the table after that div
    # table = div.find_next("table")
    # except Exception as e:
    #     print("Got error: ", e)
    #     raise e

    all_rows = table.tbody.find_all("tr")

    rows = [r for r in all_rows if r.td]

    # extract text for each cell
    dataTable = []
    for row in rows:
        if (row.get("class") and "sortbottom" in row.get("class")):
            continue

        dataRow = []
        cells = row.find_all("td")

        # print(len(cells))
        if (len(cells) < table_width):
            print("Row is < " + str(table_width) + " cells for prev_div_id: " + prev_div_id + ", and url: " + url)
            print(cells)
            continue

        # print("Row is >= 16 cells")
        for cell in cells:
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

        # print(len(dataRow))

            # dataRow.append([cell])
        if (len(dataRow) > 0):
            dataTable.append(dataRow)
            # print(len(dataRow))

            # Stub to get only one row
            # return dataTable

    return np.array(dataTable)

    # raise ValueError(f"No table found with previous div '{prev_div}'")
def get_quali_from_link(url: str):
    # TODO get the whole table, each row becomes one QualiPosition
    qualiTable:NDArray = get_table_from_wiki_following_div(url, )
    # TODO properly create instances of QualiPosition from the row
    return ClassDefinitions.Quali([]) # stub

def get_results_from_link(url: str):
    # TODO get the whole table, each row becomes one RacePosition
    # TODO properly create instances of RacePosition from the row
    return ClassDefinitions.Results([]) # stub

def get_race_from_link(url: str):
    # stub, TODO get info from the wiki page ofc
    return ClassDefinitions.Race(url, "circuit", "date",
                                 get_quali_from_link(url), get_results_from_link(url))


def get_races_from_links(urls: List[str]):
    races: List[ClassDefinitions.Race] = []
    for url in urls:
        races.append(get_race_from_link(url))

    return races

def get_F1_season_urls(url:str, table_caption: str):
    F1_seasons_table: NDArray = get_table_from_wiki_captioned(url, table_caption)
    return F1_seasons_table[:, 0, 1]

def get_F1_season(url: str, prev_div_id:str, table_width:int):
    season_table:NDArray = get_table_from_wiki_following_div("https://en.wikipedia.org" + season_link, "Grands_Prix", 6)
    season_races = np.char.add("https://en.wikipedia.org", season_table[:, -1, 1])
    return Season(season_link, get_races_from_links(season_races))


def json_to_Seasons_List(jsonArray: NDArray):
    # TODO interpret the np.loadtxt result
    return []

""" 'Main' """
All_seasons: List[ClassDefinitions.Season] = []



if os.path.exists("race_wikilinks.json"):
    All_seasons = json_to_Seasons_List(np.loadtxt("race_wikilinks.json", delimiter=",", dtype=str))
    # have to create json interpreter

else:
    print("Getting wikilinks from wiki tree")

    F1_season_names: NDArray = get_F1_season_urls("https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions", "World Drivers' Champions by season")
    print(F1_season_names)


    for season_link in F1_season_names:
        season = get_F1_season("https://en.wikipedia.org" + season_link, "Grands_Prix", 6)
        # print("Trying to find table for season ", season)
        All_seasons.append(season)

    """write to json"""

"""Now can do queries"""