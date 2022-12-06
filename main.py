import argparse
import csv
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

    args = parser.parse_args()
    args.func(args)


def find(args):
    matching_dogs = (dog[2] for dog in dog_list if dog[1] == args.name)
    print(list(matching_dogs))


if __name__ == '__main__':
    dog_list = fetch_file(2015)
    parse_arguments()