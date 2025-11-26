#!/usr/bin/python

# Feel free to modify, but do not make it public with the
# current (and valid) scopus apiKey.
#
# Author: Alexander Weigl <weigl@kit.edu> (2025)
#
# SPDX-License: GPL-v3-or-later

import os
import os.path
import sys
import shutil
import yaml
import requests
import urllib.parse
import json 
from pathlib import Path

TMP = Path("tmp/")
PUBLIC = Path("public/")
try:
    TMP.mkdir()
    PUBLIC.mkdir()
except:
    pass

with open("poeple.yml") as fh:
    CONFIG = yaml.safe_load(fh)


import requests

csv = {}  #  kit_id -> 4-Tupel
scopus_result = {}

for pi, piinfo in CONFIG.items():
    print("Processing:", pi)
    scopus_result[pi] = {"found":[], "not_found":[]}

    data = {
        "referencing":"not_referenced",
        "external_publications":"all",
        "lang":"de",
        "format":"csl_json",
        "consider_online_advance_publication_date":True,
        "consider_additional_pof_structures":True,
        "consider_suborganizations":True,
        "consider_predecessor_organizations":False,
        "year":"2021-", # filter by year
        "order":"desc year"

        # You need to put your KITopen author number in the list of contributors.
        # This number can be obtain by looking at the created queries of
        #    https://publikationen.bibliothek.kit.edu/publikationslisten
        # "Publikationen exportieren als ..." > "csl_json" and then looking for "contributors".

        , "contributors":f"[[[],[\"{piinfo['kit']}\"]]]"

        # , "programnumber":"6405.105" # Topic ESS (46.23)
    }


    result = requests.post("https://publikationen.bibliothek.kit.edu/publikationslisten/get.php", data)

    for r in result.json():
        if r["type"] not in ('dataset', 'report', 'speech', 'thesis', 'motion_picture'):
            print("* ",r["kit-publication-id"], r["type"], r["title"])

            title = r['title']
            scopus_search="https://api.elsevier.com/content/search/scopus"
            params = {
                "query": f"TITLE (\"{title}\")",
                "apiKey": os.environ["SCOPUS_API_KEY"]
            }

            scopus_data  = requests.get(scopus_search, params).json()

            try:
                data = scopus_data['search-results']['entry'][0]
                if "error" in data:
                    scopus_result[pi]["not_found"].append(title)
                    continue
                else:
                    csv[r['kit-publication-id']] = (
                        r['kit-publication-id'],
                        data['dc:identifier'][10:],
                        data['prism:coverDisplayDate'],
                        data['dc:title'],
                        data['prism:publicationName'],
                    )
    
                    
                    scopus_result[pi]["found"].append({
                        "SCOPUS-ID": data['dc:identifier'][10:],
                        "KIT-ID": r['kit-publication-id'],
                        "TITLE": data['dc:title'],
                        "VENUE": data['prism:publicationName'],
                        "DATE": data['prism:coverDisplayDate'],
                    })
            except:
                pass


json.dump(scopus_result, (TMP/"scopus.json").open("w"), indent=2, ensure_ascii=False)

with (PUBLIC/"scopus.csv").open("w") as fh:
    fmt = '"%s";"%s";"%s";"%s";"%s"\n'
    fh.write(fmt%("KIT-ID", "SCOPUS-ID", "YEAR", "TITLE", "VENUE"))
    for entry in csv.values():
        fh.write(fmt % entry)
