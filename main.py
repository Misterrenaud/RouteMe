import json
import os.path
from copy import deepcopy
from dataclasses import dataclass
from itertools import cycle
import operator
from time import sleep

import requests

from strava import get_access_token

ONE_KM_IN_DEGREES = 0.015060


@dataclass
class Coordinates:
    lat: float
    lon: float


def norm_lat(lat: float):
    return abs((lat - 90) % 360 - 180) - 90


def norm_lon(lon: float):
    return ((lon + 180) % 360) - 180


class Square:
    def __init__(self, center: Coordinates):
        self.center = center

    def get_array(self):
        """
        The latitude and longitude for two points describing a rectangular boundary for the search: [southwest corner
        latitutde, southwest corner longitude, northeast corner latitude, northeast corner longitude]
        """
        return [
            norm_lat(self.center.lat - ONE_KM_IN_DEGREES / 2),
            norm_lon(self.center.lon - ONE_KM_IN_DEGREES / 2),
            norm_lat(self.center.lat + ONE_KM_IN_DEGREES / 2),
            norm_lon(self.center.lon + ONE_KM_IN_DEGREES / 2),
        ]


def snail_generator(start: Coordinates, step=ONE_KM_IN_DEGREES):
    signe_gen = cycle([operator.add, operator.add, operator.sub, operator.sub])
    direc_gen = cycle(["lon", "lat"])
    count = 1
    point = deepcopy(start)
    yield start
    while True:
        for _ in range(2):
            direct = next(direc_gen)
            signe = next(signe_gen)
            for _ in range(count):
                point.__dict__[direct] = signe(point.__dict__[direct], step)
                yield point
        count += 1


if __name__ == '__main__':
    with open("conf.json") as fp:
        conf = json.load(fp)

    start = Coordinates(*conf["start"])

    already_done = 0

    if os.path.exists("segments.jsons"):
        with open("segments.jsons", "r") as fp:
            already_done = int(len(fp.readlines()) / 2)
            print(f"skipping {already_done} squares")

    for i, p in enumerate(snail_generator(start)):
        if i < already_done:
            continue

        square = Square(p).get_array()
        print(f"requesting square {p}")

        response = requests.get(
            url="https://www.strava.com/api/v3/segments/explore",
            headers={"Authorization": f"Bearer {get_access_token()}"},
            params={
                "bounds": ",".join([str(x) for x in square]),
                "activity_type": "riding",
            }
        )
        if response.status_code == 200:
            for x in response.json()["segments"]:
                print(x["name"], x["start_latlng"])
            with open("segments.jsons", "a") as fp:
                json.dump(square, fp)
                fp.write("\n")
                json.dump(response.json(), fp)
                fp.write("\n")
        else:
            print(response.json())
            print("15min pause")
            sleep(60*15)


