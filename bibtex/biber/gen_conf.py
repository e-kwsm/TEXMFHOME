#!/usr/bin/env python3
"""generate biber.conf
"""
import argparse
import csv
import logging
from typing import TextIO
from xml.dom import minidom


logging.basicConfig(level=logging.INFO)


def abbreviate_jounals(infile: TextIO, outfile: TextIO) -> None:
    """abbreviate jounal titles
    """
    doc = minidom.Document()
    node_config = doc.createElement("config")
    doc.appendChild(node_config)

    node_sourcemap = doc.createElement("sourcemap")
    node_config.appendChild(node_sourcemap)

    node_maps = doc.createElement("maps")
    node_maps.setAttribute("datatype", "bibtex")
    node_sourcemap.appendChild(node_maps)

    node_map = doc.createElement("map")
    node_map.setAttribute("map_overwrite", "1")
    node_maps.appendChild(node_map)

    node_map_step = doc.createElement("map_step")
    node_map_step.setAttribute("map_field_source", "doi")
    node_map_step.setAttribute("map_match", r"https?://[^/]+/(\S+)\s*$")
    node_map_step.setAttribute("map_replace", "$1")
    node_map.appendChild(node_map_step)

    logging.info("read {}".format(infile.name))
    with infile:
        for row in csv.reader(infile, delimiter="\t"):
            if row[0][0] == "#":
                continue
            journal, abbr = row
            for old, new in [
                [" ", r"\s+"],
                [".", r"\."],
                ["(", r"\("],
                [")", r"\)"],
                ["&", r"\\&"],
            ]:
                journal = journal.replace(old, new)
            journal = r"^\s*" + journal + r"\s*$"
            node_map_step = doc.createElement("map_step")
            node_map_step.setAttribute("map_field_source", "journal")
            node_map_step.setAttribute("map_match", journal)
            node_map_step.setAttribute("map_replace", abbr)
            node_map.appendChild(node_map_step)

    logging.info("write {}".format(outfile.name))
    with outfile:
        doc.writexml(outfile, addindent="  ", newl="\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", nargs="?", default="journal_list.tsv", type=argparse.FileType(),
                        help="CSV of abbreviations")
    parser.add_argument("outfile", nargs="?", default="biber.conf",
                        type=argparse.FileType("w", encoding="UTF-8"), help="biber.conf")
    args = parser.parse_args()
    abbreviate_jounals(**vars(args))


if __name__ == "__main__":
    main()
