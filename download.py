#!/usr/bin/python

import os
import os.path
import sys
import shutil
import yaml
import requests
import urllib.parse
from time import sleep

from pathlib import Path

TMP = Path("tmp/")
try:
    TMP.mkdir()
except:
    pass

with open("poeple.yml") as fh:
    CONFIG = yaml.safe_load(fh)


def download_to(url, fil, desc=""):
    print("\t",desc,end="")

    status = 1
    tries = 10

    while status != 200 and tries > 0:
        tries -= 1
        r = requests.get(url, allow_redirects=True)

        if r.status_code == 200: break
        
        if r.status_code == 429: # To Many Requests on DBLP. Rate Limit triggered
            # After FAQ the header should be set, but is not ra = r.headers['Retry-After']
            print("RATE LIMIT. I am waiting.", (10-tries)*2)
            sleep((10-tries)*2)
        status = r.status_code
    
    open(fil, 'wb').write(r.content)
    print(" ok")

KIT_TAGGING="kit_tagging=11784.105OR11825.105OR11785.105OR11786.105OR11829.105OR11889.105OR11938.105OR11980.105OR11965.105"

def _fetch(name, kit_id, dblp_id):
    print(f"Download data for {name}")

    download_to(f"https://dblp.uni-trier.de/pid/{dblp_id}.xml", TMP/f"{name}.xml",
                desc = "DBLP")

    all_pubs=f"https://publikationen.bibliothek.kit.edu/publikationslisten/get.php?referencing=all&external_publications=all&lang=de&format=csl_json&style=kit-3lines-title_b-authors-other&consider_suborganizations=true&contributors=%5B%5B%5B%221000.105%22%5D%2C%5B%22{kit_id}%22%5D%5D%5D&year=2021-"

    download_to(all_pubs, TMP/f"{name}_all.json", desc="KIT Library")
    download_to(f"{all_pubs}&{KIT_TAGGING}", TMP/f"{name}_kikit.json", desc="KiKIT tagged")
    # TOPIC ESS
    #download_to(f"{all_pubs}&programnumber=6405.105", TMP/f"{name}_ESS.json", desc="Topic ESS")
    download_to(f"{all_pubs}&programnumber=is_not_empty", TMP/f"{name}_ESS.json", desc="Topic ESS")

for pi, data in CONFIG.items():
    _fetch(pi, data['kit'], data['dblp'])



#https://publikationen.bibliothek.kit.edu/publikationslisten/?referencing=all&external_publications=all&lang=de&format=html&style=kit-3lines-title_b-authors-other&consider_online_advance_publication_date=false&consider_additional_pof_structures=false&consider_suborganizations=true&consider_predecessor_organizations=false&contributors=%5B%5B%5B%5D%2C%5B%22nNadja%20Klein%22%5D%5D%5D

#https://publikationen.bibliothek.kit.edu/publikationslisten/?referencing=all&external_publications=all&lang=de&format=html&style=kit-3lines-title_b-authors-other&consider_online_advance_publication_date=false&consider_additional_pof_structures=false&consider_suborganizations=true&consider_predecessor_organizations=false&contributors=%5B%5B%5B%221000.105%22%5D%2C%5B%22nNadja%20Klein%22%5D%5D%5D

#https://publikationen.bibliothek.kit.edu/publikationslisten/?referencing=all&external_publications=all&lang=de&format=html&style=kit-3lines-title_b-authors-other&consider_suborganizations=true&consider_online_advance_publication_date=false&consider_additional_pof_structures=false&consider_predecessor_organizations=false&programnumber=6405.105
