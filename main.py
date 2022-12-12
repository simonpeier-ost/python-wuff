import argparse
import csv
import datetime
import pathlib
import random
import shutil
from collections import Counter

import requests
from rich import print
from rich.table import Table


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

    parser_find = subparsers.add_parser("find", help="find all dogs matching a name")
    parser_find.add_argument("name", type=str)
    parser_find.add_argument("-y", "--year", default=datetime.datetime.now().year,
                             help="year to get data from")
    parser_find.set_defaults(func=find)

    parser_stats = subparsers.add_parser("stats", help="show various stats about the dogs")
    parser_stats.add_argument("-y", "--year", default=datetime.datetime.now().year,
                              help="year to get data from")
    parser_stats.set_defaults(func=stats)

    parser_create = subparsers.add_parser("create", help="create a new dog")
    parser_create.add_argument("-o", "--output-dir", type=str, default=None,
                               help="directory where the downloaded file should be put")
    parser_create.add_argument("-y", "--year", default=datetime.datetime.now().year,
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
    if type(args.year) is int:
        dog_list = fetch_file(args.year)

        name = random.choice([dog[1] for dog in dog_list])
        year = random.choice([dog[2] for dog in dog_list])
        sex = random.choice(["m", "f"])
        path = args.output_dir
        media_filename = download_dog_media_file(name, year, path)

        print("[bold underline]Here's your new dog![/bold underline] :dog:")
        print(f"[bold]Name:[/bold] [cyan]{name}[/cyan]")
        print(f"[bold]Birth year:[/bold] [magenta]{year}[/magenta]")
        print(f"[bold]Sex:[/bold] {sex}")
        print(f"[bold]The image of the new dog can be found here:[/bold] {media_filename}")
    else:
        print(year_error_message)


def print_find_table(row_list):
    table = Table(title="Matching dogs")
    table.add_column("Name", style="cyan")
    table.add_column("Birth year", style="magenta")
    table.add_column("Sex")

    for element in row_list:
        table.add_row(str(element[0]), str(element[1]), str(element[2]))

    print(table)


def find(args):
    if type(args.year) is int:
        dog_list = fetch_file(args.year)
        matching_dogs = ([dog[1], dog[2], dog[4][0]] for dog in dog_list if dog[1] == args.name)
        print_find_table(matching_dogs)
    else:
        print(year_error_message)


def print_most_common_names_table(title, row_list):
    table = Table(title=str(title))
    table.add_column("Name", style="cyan")
    table.add_column("Age", style="magenta")

    for element in row_list:
        table.add_row(str(element[0]), str(element[1]))

    print(table)
    print("\n")


def stats(args):
    if type(args.year) is int:
        dog_list = fetch_file(args.year)

        overall = [dog[1] for dog in dog_list if "?" not in dog[1]]
        male = [dog[1] for dog in dog_list if dog[3] == 1]
        female = [dog[1] for dog in dog_list if dog[3] == 2]

        print("[bold underline]Statistics[/bold underline] :bar_chart:\n")
        print(f"[bold]Shortest name:[/bold] [cyan]{min(overall, key=len)}[/cyan]")
        print(f"[bold]Longest name:[/bold] [cyan]{max(overall, key=len)}[/cyan]")
        print(f"[bold]Number of male dogs:[/bold] [not bold magenta]{len(male)}[/not bold magenta]")
        print(f"[bold]Number of female dogs:[/bold] [not bold magenta]{len(female)}[/not bold magenta]")
        print("[bold]10 most common names:[/bold]\n")
        print_most_common_names_table("Overall", Counter(overall).most_common(10))
        print_most_common_names_table("Male", Counter(male).most_common(10))
        print_most_common_names_table("Female", Counter(female).most_common(10))
    else:
        print(year_error_message)


if __name__ == "__main__":
    year_error_message = "The entered year is not a number"
    parse_arguments()
