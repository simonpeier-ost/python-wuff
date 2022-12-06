import argparse
import csv
from collections import Counter

import requests


def fetch_file(year):
    url = 'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen_od1002/download/KUL100OD1002.csv'
    response = requests.get(url)
    response.encoding = "utf-8-sig"

    dogs = []
    reader = csv.DictReader(response.text.splitlines())
    for row in reader:
        if int(row["StichtagDatJahr"]) == year:
            dogs.append([row["StichtagDatJahr"], row["HundenameText"], row["GebDatHundJahr"], int(row["SexHundCd"]),
                         row["SexHundLang"], row["SexHundSort"], row["AnzHunde"]])
    return dogs


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_find = subparsers.add_parser("find")
    parser_find.add_argument('name', type=str)
    parser_find.set_defaults(func=find)

    parser_stats = subparsers.add_parser("stats")
    parser_stats.set_defaults(func=stats)

    args = parser.parse_args()
    args.func(args)


def find(args):
    matching_dogs = ([dog[1], dog[2], dog[4][0]] for dog in dog_list if dog[1] == args.name)
    print(list(matching_dogs))


def stats(args):
    overall = (dog[1] for dog in dog_list)
    male = (dog[1] for dog in dog_list if dog[3] == 1)
    female = (dog[1] for dog in dog_list if dog[3] == 2)
    print("10 most common names")
    print(f"Overall: {Counter(overall).most_common(10)}")
    print(f"Male: {Counter(male).most_common(10)}")
    print(f"Female: {Counter(female).most_common(10)}")


if __name__ == '__main__':
    dog_list = fetch_file(2015)
    parse_arguments()
