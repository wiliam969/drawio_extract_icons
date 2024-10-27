# this file will extract icons and add them in the correct format

import os

# importing required modules 
from zipfile import ZipFile 
import xml.etree.cElementTree as ET

import glob
import argparse
import os

# required arg
import json

import base64

from collections import defaultdict
import xml
import re

icons = defaultdict(list)
categories = set()

def extract_nested_zip(zippedFile, toFolder):
    """ Unzip a zip file and its contents, including nested zip files
        Delete the zip file(s) after extraction
    """
    with ZipFile(zippedFile, 'r') as zfile:
        zfile.extractall(path=toFolder,members=(member for member in zfile.namelist() if member.endswith('.png') or member.endswith('.svg') or member.endswith('.jpg')))
    os.remove(zippedFile)
    for root, dirs, files in os.walk(toFolder):
        for filename in files:
            if re.search(r'\.zip$', filename):
                fileSpec = os.path.join(root, filename)
                extract_nested_zip(fileSpec, root)


def get_size(file_path, unit='bytes'):
    file_size = os.path.getsize(file_path)
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        raise ValueError("Must select from \
        ['bytes', 'kb', 'mb', 'gb']")
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)

def get_width_height(icon):
    try:
        tree = ET.parse(icon)
        root = tree.getroot()
        viewBox = root.attrib["viewBox"]
        width, height = viewBox.split(" ")[2:]
        return float(width), float(height)
    except KeyError:
        if "height" in root.attrib.keys():
            height = root.attrib["height"]
        else:
            height = 100
        if "width" in root.attrib.keys():
            width = root.attrib["width"]
        else:
            width = 100
        return float(width), float(height)
    except xml.etree.ElementTree.ParseError:
        return float(100), float(100)

def find_files_and_add_2_list(folder):
    for root, dirs, files in os.walk(folder):
        for filename in files:
            
            category = root.replace("tmp_icons/", "")
            category = category.split("\\") [0]
            
            nice_title = root.replace("\\", " ")

            w, h = get_width_height(root + "\\" + filename)
            item = {
                "title": f"{nice_title} | ",
                "data": "data:image/svg+xml;base64,"
                + base64.b64encode(open(root + "\\" + filename, "rb").read()).decode("utf-8"),
                "w": w,
                "h": h,
                "aspect": "fixed",
            }

            icons[category].append(item)

entries = os.listdir('icons/')

for entry in entries: 
    name = entry.replace(".zip","")
    extract_nested_zip('icons/' + entry, "tmp_icons")



    find_files_and_add_2_list("tmp_icons/" + name)

    drawio = {}
    for category in icons.keys():
        with open(
            "./gen_templates/biorender-" + category.replace(" ", "_") + ".xml", "w"
        ) as outfile:
            outfile.write("<mxlibrary>" + json.dumps(icons[category]) + "</mxlibrary>")
        file_size = get_size( "./gen_templates/biorender-" + category.replace(" ", "_") + ".xml", "mb")
        if file_size <50:
            drawio[category] = {"n":len(icons[category]), "file": "Bioicons-" + category.replace(" ", "_") + ".xml"}
        else:
            print(category.replace(" ", "_"), "is too big", file_size, "MB")
            os.remove("./gen_templates/biorender-" + category.replace(" ", "_") + ".xml")


# with open('../drawio-lib/categories.json', 'w') as outfile:
#         json.dump(drawio, outfile)