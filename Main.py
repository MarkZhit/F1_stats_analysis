""" Sources """
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
                print("url: " + url)
                # print("row: " + row)
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


def get_table_from_wiki_following_div(url: str, prev_div: str) -> NDArray:
    headers = {"User-Agent": "Mozilla/5.0"}  # looks like a browser
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find the div containing the text prev_div
    div = soup.find("h3", string=prev_div)
    table = div.find_next("table")

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
        if (len(cells) < 6):
            print("Row is < 6 cells")
            print("url: " + url)
            # print("row: " + row)
            # print(rows.index(row))
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
F1_seasons_table: NDArray = get_table_from_wiki_captioned("https://en.wikipedia.org/wiki/List_of_Formula_One_World_Drivers%27_Champions", "World Drivers' Champions by season")
# print(F1_seasons_table)
F1_seasons = F1_seasons_table[:, 0, 1]
# print(F1_seasons)



"""NEED TO GO BY RESULTS AND STANDINGS INSTEAD"""

All_races = []
for season in F1_seasons:
    # print("Trying to find table for season ", season)
    season_table = get_table_from_wiki_following_div("https://en.wikipedia.org" + season, "Grands Prix")
    # print(season_table)
    season_races = season_table[:, -1, 1]
    # print(season_races)
    All_races.append(season_races)
    # print("races found")
    # break
print(All_races)

# season94_table = get_table_from_wiki_following_div("https://en.wikipedia.org/wiki/1994_Formula_One_World_Championship", "Calendar")
# print(season94_table)
# season94_races = season94_table[:, 0, 1]
# print(season94_races)
# season95_table = get_table_from_wiki_following_div("https://en.wikipedia.org/wiki/1995_Formula_One_World_Championship", "Calendar")
# print(season95_table)
# season95_races = season95_table[:, 0, 1]
# print(season95_races)