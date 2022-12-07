import argparse
import csv
import datetime
import pathlib
import random
import shutil
from collections import Counter

import requests


def fetch_file(year):
    url = "https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen_od1002/download/KUL100OD1002.csv"
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
    parser_find.add_argument("name", type=str)
    parser_find.add_argument("-y", "--year", type=int, default=datetime.datetime.now().year,
                             help="year to get data from")
    parser_find.set_defaults(func=find)

    parser_stats = subparsers.add_parser("stats")
    parser_stats.add_argument("-y", "--year", type=int, default=datetime.datetime.now().year,
                              help="year to get data from")
    parser_stats.set_defaults(func=stats)

    parser_create = subparsers.add_parser("create")
    parser_create.add_argument("-o", "--output-dir", type=str, default=None)
    parser_create.add_argument("-y", "--year", type=int, default=datetime.datetime.now().year,
                               help="year to get data from")
    parser_create.set_defaults(func=create_new_dog)

    args = parser.parse_args()
    args.func(args)


def download_dog_media_file(name, year, path):
    # Get link of random dog media file
    res = requests.get("https://random.dog/woof.json").json()
    media_url = res["url"]

    # Download said dog media file
    file_extension = pathlib.Path(media_url).suffix
    filename = f"{name}_{year}{file_extension}"
    out_path = (pathlib.Path(path) if path else pathlib.Path.cwd()) / filename
    res = requests.get(media_url, stream=True)
    if res.status_code == 200:
        with open(out_path, "wb") as file:
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, file)

    return out_path


def create_new_dog(args):
    dog_list = fetch_file(args.year)

    name = random.choice([dog[1] for dog in dog_list])
    year = random.choice([dog[2] for dog in dog_list])
    sex = random.choice(["m", "f"])
    path = args.output_dir
    media_filename = download_dog_media_file(name, year, path)

    print("Here's your new dog!")
    print(f"Name: {name}")
    print(f"Birth year: {year}")
    print(f"Sex: {sex}")
    print(f"The image of the new dog can be found here: {media_filename}")


def find(args):
    dog_list = fetch_file(args.year)

    matching_dogs = ([dog[1], dog[2], dog[4][0]] for dog in dog_list if dog[1] == args.name)
    print(list(matching_dogs))


def stats(args):
    dog_list = fetch_file(args.year)

    overall = [dog[1] for dog in dog_list if "?" not in dog[1]]
    male = [dog[1] for dog in dog_list if dog[3] == 1]
    female = [dog[1] for dog in dog_list if dog[3] == 2]

    print(f"Shortest name: {min(overall, key=len)}")
    print(f"Longest name: {max(overall, key=len)}")
    print("10 most common names")
    print(f"Overall: {Counter(overall).most_common(10)}")
    print(f"Male: {Counter(male).most_common(10)}")
    print(f"Female: {Counter(female).most_common(10)}")
    print(f"Number of male dogs: {len(male)}")
    print(f"Number of female dogs: {len(female)}")


if __name__ == "__main__":
    parse_arguments()
