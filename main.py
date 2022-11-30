import csv
import requests


def print_hello():
    print(f'Hello World')


def fetch_file(year):
    url = 'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen_od1002/download/KUL100OD1002.csv'
    response = requests.get(url)
    response.encoding = "utf-8-sig"

    dogs = []
    reader = csv.DictReader(response.text.splitlines())
    for row in reader:
        if int(row["StichtagDatJahr"]) == year:
            dogs.append((row["StichtagDatJahr"], row["HundenameText"], row["GebDatHundJahr"], row["SexHundCd"],
                         row["SexHundLang"], row["SexHundSort"], row["AnzHunde"]))
    return dogs


if __name__ == '__main__':
    print(fetch_file(2015))
