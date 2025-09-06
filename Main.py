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
        for i, row in enumerate(rows):
            dataRow = []
            cells = row.find_all("td")
            if (len(cells) < 16):
                # print("Row is < 16 cells, i=",str(i)," url is: ", url)
                # figured out how to handle it
                currCells = cells
                cells = rows[i - 1].find_all("td")
                cells[3] = currCells[0]
                cells[4] = currCells[1]
                cells[5] = currCells[2]
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
            dataTable.append(dataRow)

        return np.array(dataTable)

    raise ValueError(f"No table found with caption '{table_caption}'")



    # raise ValueError(f"No table found with previous div '{prev_div}'")

    # return Results([]) # stub




def get_F1_season_urls(url:str, table_caption: str):
    F1_seasons_table: NDArray = get_table_from_wiki_captioned(url, table_caption)
    return F1_seasons_table[:, 0, 1]

def json_to_Seasons_List(jsonArray: NDArray):
    # TODO interpret the np.loadtxt result
    return

""" 'Main' """
All_seasons: List[Season] = []



if os.path.exists("race_wikilinks.json"):
    All_seasons = json_to_Seasons_List(np.loadtxt("race_wikilinks.json", delimiter=",", dtype=str))
    # have to create json interpreter

else:
    print("Getting wikilinks from wiki tree")

    F1_season_names: NDArray = get_F1_season_urls("https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions", "World Drivers' Champions by season")
    # print(F1_season_names)


    for season_link in F1_season_names:
        season:Season = Season.get_F1_season("https://en.wikipedia.org" + season_link, "Grands_Prix")
        # print("Trying to find table for season ", season)
        All_seasons.append(season)

    """write to json"""

"""Now can do queries"""
