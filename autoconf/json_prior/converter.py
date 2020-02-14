import json


def convert(directory):
    with open(f"{directory}.json", "w+") as f:
        json.dump({}, f)
