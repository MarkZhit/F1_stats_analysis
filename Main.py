""" Sources """
from numpy.f2py.auxfuncs import throw_error

# https://medium.com/pipeline-a-data-engineering-resource/how-i-used-python-to-scrape-100-tables-containing-5-years-of-f1-data-2e64125903c8
# ^ explains concept for webscraping

# https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions
# ^ contains a table with the list of f1 seasons by year (with wiki links)
# https://en.wikipedia.org/wiki/2000_Formula_One_World_Championship
# ^ year, contains a table with list of people and races (with wiki links)
# https://en.wikipedia.org/wiki/2000_Australian_Grand_Prix
# ^ individual race, contains quali and race results in two separate tables


""" imports """
import requests
from bs4 import BeautifulSoup
# import pandas as pd
import numpy as np
from numpy.typing import NDArray
import re
import os

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
    headers = {"User-Agent": "Mozilla/5.0"}  # looks like a browser
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

""" Code """
All_races = []

try:
    All_races = np.loadtxt("race_wikilinks.csv", delimiter=",", dtype=str)

except Exception as e:
    print("wikilinks csv not found, caught error: ", e)
    print("Getting wikilinks from wiki tree")

    F1_seasons_table: NDArray = get_table_from_wiki_captioned("https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions", "World Drivers' Champions by season")
    # print(F1_seasons_table)
    F1_seasons = F1_seasons_table[:, 0, 1]
    # print(F1_seasons)

    for season in F1_seasons:
        # print("Trying to find table for season ", season)
        season_table:NDArray = get_table_from_wiki_following_div("https://en.wikipedia.org" + season, "Grands_Prix", 6)
        # print(season_table)
        season_races = season_table[:, -1, 1]
        # print(season_races)
        All_races.extend(list(season_races))
        # print("races found")
        # break
    All_races = np.char.add("https://en.wikipedia.org", All_races)
    np.savetxt("race_wikilinks.csv", All_races, delimiter=",", fmt="%s")

# I want these properties:
# each row  has the second element be a whole table
# This table contains qualifying results
# quali results has rows of position, then columns are: driver name, constructor name, Q1, Q2, Q3, quali position
# each row  has the third element be a whole table
# This table contains GP results
# race results has rows of position, then columns are: driver name, constructor name, laps completed, final time/extra laps/retirement, points gained

All_qualis = []
All_results = []

for race in All_races:
    try:
        #1950 british gp seems to be different, it uses Race_Classification and Qualifying_Classification isntead
        #1950 indianapolis500 has a box score instead
        #1950s have two drivers for one car ig, have to figure out how to deal with that. maybe combine them into one person?
        quali_table = get_table_from_wiki_following_div(race, "Qualifying", 4)
        results_table = get_table_from_wiki_following_div(race, "Race",7)
        All_qualis.append(quali_table)
        All_results.append(results_table)
    except Exception as e:
        print("Got exception: ", e, "for race link: ", race)


All_info = np.hstack([All_races, All_qualis, All_results])  # shape (N, 3)

# print(All_races)
