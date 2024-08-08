#!/usr/bin/python

import os
import os.path
import sys
import shutil
import yaml
import requests
import urllib.parse

from pathlib import Path

TMP = Path("tmp/")
try:
    TMP.mkdir()
except:
    pass

with open("poeple.yml") as fh:
    CONFIG = yaml.safe_load(fh)


def download_to(url, fil):
    r = requests.get(url, allow_redirects=True)
    open(fil, 'wb').write(r.content)

KIT_TAGGING="kit_tagging=11784.105OR11825.105OR11785.105OR11786.105OR11829.105OR11889.105OR11938.105OR11980.105OR11965.105"

def _fetch(name, kit_id, dblp_id):
    print(f"Download data for {name}")

    print(f"\tDBLP", end=" ")
    download_to(f"https://dblp.uni-trier.de/pid/{dblp_id}.xml", TMP/f"{name}.xml")
    print(f"ok\n\tKIT all", end=" ")
    all_pubs=f"https://publikationen.bibliothek.kit.edu/publikationslisten/get.php?referencing=all&external_publications=all&lang=de&format=csl_json&style=kit-3lines-title_b-authors-other&consider_suborganizations=true&contributors=%5B%5B%5B%5D%2C%5B%22{kit_id}%22%5D%5D%5D&year=2021-2024"

    download_to(all_pubs, TMP/f"{name}_all.json")
    print(f"ok\n\tKIT KiKIT", end=" ")
    download_to(f"{all_pubs}&{KIT_TAGGING}", TMP/f"{name}_kikit.json")
    print(f"ok")


for pi, data in CONFIG.items():
    _fetch(pi, data['kit'], data['dblp'])

