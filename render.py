#!/usr/bin/python

from collections import namedtuple
import os
import os.path
import sys
import shutil
import yaml
import json
import xml.etree.ElementTree as ET
from pprint import pprint

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("_layouts"),
    autoescape=select_autoescape()
)

TMP = Path("tmp/")
PUBLIC = Path("public/")
CFG = Path("config.yml")

with open("poeple.yml") as fh:
    CONFIG = yaml.safe_load(fh)

class BibEntry:
    title: str
    doi: str
    year: str
    kit_id: str = None

    def __init__(self, title, doi, year=0):
        self.title, self.doi, self.year = (title, doi, int(year))

    def __eq__(self, other):
        if isinstance(other, BibEntry):
            return self.doi == other.doi
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __hash__(self):
        return hash(self.doi)


def render():
    for pi, data in CONFIG.items():
        _render(pi)

    render_index()

def _readjson(f):
    def as_bib_entry(jpub):
        e =  BibEntry(jpub['title'], jpub.get('DOI','n/a'), jpub['issued']['date-parts'][0][0])
        e.kit_id = jpub['kit-publication-id']
        return e

    try:
        with open(f) as f:
            dt = json.load(f)
            return list(map(as_bib_entry, dt))
    except Exception as e:
        print(f"Error {e} reading file {f}")
        return []

def _readxml(f):
    def as_bib_entry(x):
        x = x[0]
        year = x.find('year').text
        title = x.find('title').text
        try:
            doi = x.find('ee').text[16:]
        except:
            print(f"No DOI in {title}")
            return None
        return BibEntry(title, doi, year)

    with open(f) as fh:
        root = ET.fromstring(fh.read())
        pubs = root.findall("r")

        pubs = filter(lambda x: x[0].find('year').text in ('2021', '2022', '2023', '2024'),
                      pubs)
        return list(filter(lambda x: x is not None, map(as_bib_entry, pubs)))


ENTRIES = {}

def _render(name):
    global ENTRIES

    bib = _readjson(TMP/f"{name}_all.json")
    kikit = _readjson(TMP/f"{name}_kikit.json")
    tess = _readjson(TMP/f"{name}_ESS.json")
    dblp = _readxml(TMP/f"{name}.xml")

    def mk_entry(b):
        a = BibEntry(b.title, b.doi, b.year)
        a.dblp = b in dblp
        a.kit = b in bib
        a.kikit = b in kikit
        a.ess = b in tess
        if a.kit:
            a.kit_id = next(x for x in bib if x.doi == b.doi).kit_id
        return a

    everything = set(bib + kikit + dblp + tess)         # remove duplicates
    entries    = list(map(mk_entry, everything)) # lift to entries
    entries.sort(key = lambda x: -x.year)
    ENTRIES[name] = entries

    template = env.get_template("pi.html")

    with open(PUBLIC/f"{name}.html", 'w') as fh:
        fh.write(template.render(name=name,dblp=dblp, bib=bib, kikit=kikit, entries=entries, pis=CONFIG))

    with open(PUBLIC/f"{name}.csv", 'w', newline='') as fh:
        import csv
        writer = csv.writer(fh, dialect='excel')
        writer.writerow(("Title", "DOI", "KIT-Id", "Year", "DBLP", "Library", "KiKIT", "Topic ESS"))
        for entry in entries:
            writer.writerow((
                entry.title,
                entry.doi,
                entry.kit_id,
                entry.dblp,
                entry.kit,
                entry.ess,
                entry.kikit,
            ))

def render_index():
    Line = namedtuple("YEARS", "everything, dblp, kit, kikit, ess")
    PI = namedtuple("PI", "name, years, all")
    data = []

    def aggregate(entries):
        dblp  = len([x for x in entries if x.dblp])
        kit   = len([x for x in entries if x.kit])
        kikit = len([x for x in entries if x.kikit])
        ess   = len([x for x in entries if x.ess])
        return Line(len(entries), dblp, kit, kikit, ess)

    def aggregate_year(entries, year):
        return aggregate([x for x in entries if x.year == year])

    for name, entries in ENTRIES.items():
        data.append(PI(name,
                       { x : aggregate_year(entries, x) for x in range(2021,2025)},
                       aggregate(entries)))

    template = env.get_template("index.html")
    with open(PUBLIC/f"index.html", 'w') as fh:
        fh.write(template.render(data=data))


def render_css():
    import sass
    content = sass.compile(dirname=("_static","public"), output_style="compressed")
    print(content)
    #with open(PUBLIC/"style.css", 'w') as fh:
    #    fh.write(content)



def main():
    #if PUBLIC.exists():
    #    shutil.rmtree(PUBLIC)
    #PUBLIC.mkdir()
    render()


if __name__ == '__main__':
    main()
