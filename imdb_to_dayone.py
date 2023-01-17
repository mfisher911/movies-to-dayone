#!/usr/bin/env python3
"""Command-line tool to create a templatized Day One entry

Basically a re-implementation of my iOS shortcut."""

import json
import logging
import urllib.parse
import urllib.request
import shutil
import subprocess
import sys


def store(row):
    """Actually save the info to DayOne"""
    args = ["dayone2", "--journal", "Journal"]
    summary = "\n"
    if row["summary"] != "N/A":
        summary = f"\n{row['summary']}"
    rating = f"{row['score']}/5"
    entry = f"# {row['title']}\n{rating}\n{summary}\n-- {row['url']}"

    tags = ["--tags", "Movies", rating]
    if row["first_viewing"]:
        tags.append("first-watch")

    args.extend(tags)

    if _path := shutil.which("corelocationcli"):
        res = subprocess.run(args=[_path], capture_output=True)
        coord = str(res.stdout, "utf8")
        args.extend(["--coordinate"] + list(coord.strip().split()))

    args.extend(["--", "new"])

    logger.debug("STDOUT: %s\nargs: %s", entry, " ".join(args))
    subprocess.run(
        args=args, input=entry, check=True, capture_output=True, text=True
    )
    subprocess.call(["/usr/bin/open", "/Applications/Day One.app"])


def main():
    """Get user input and store the info to DayOne"""
    if "https:" in sys.argv[1]:
        url = sys.argv[1]
    else:
        url = input("IMDb URL: ")
    url = url.strip().replace("/reference", "")
    score = input("Rating: ").strip()
    is_new = input("First viewing (y/N): ")
    first_viewing = is_new.strip().casefold() == "y"
    data = f"input={url}".encode("utf-8")
    req = urllib.request.Request(
        "https://shell.themfishers.com/imdb/", data=data, method="POST"
    )

    with urllib.request.urlopen(req) as f:
        resp = f.read().decode("utf-8")

    info = json.loads(resp)
    info["score"] = score
    info["first_viewing"] = first_viewing
    store(info)
    letterboxd = urllib.parse.quote_plus(info["letterboxd_title"])
    print(f"<https://letterboxd.com/search/{letterboxd}/>")
    print(f"<https://trakt.tv/search?query={letterboxd}>")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger()
    main()
