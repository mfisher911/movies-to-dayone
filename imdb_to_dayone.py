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

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def make_entry(row):
    """Format the row info for Day One."""
    summary = "\n"
    if row["summary"] != "N/A":
        summary = f"\n{row['summary']}"
    rating = f"{row['score']}/5"
    us_title = f"\n*{row['title']}*" if row.get("foreign_title") else ""
    entry = f"""# {row['original_title']} ({row['year']}){us_title}
{rating}
{summary}
-- {row['url']}"""

    return entry, rating


def store(row):
    """Actually save the info to DayOne"""
    args = ["dayone2", "--journal", "Journal"]

    (entry, rating) = make_entry(row)

    tags = ["--tags", "Movies", rating]
    if row["first_viewing"]:
        tags.append("first-watch")

    args.extend(tags)

    if _path := shutil.which("corelocationcli"):
        try:
            res = subprocess.run(
                args=[_path], check=True, text=True, capture_output=True
            )
            if coord := res.stdout.strip():
                args.extend(["--coordinate"] + list(coord.split()))
        except subprocess.CalledProcessError:
            print("    Could not get coordinates with corelocationcli")

    args.extend(["--", "new"])

    logger.debug("STDOUT: %s\nargs: %s", entry, " ".join(args))
    subprocess.run(
        args=args, input=entry, check=True, capture_output=True, text=True
    )
    subprocess.call(["/usr/bin/open", "/Applications/Day One.app"])


def main():
    """Get user input and store the info to DayOne"""
    # a little convoluted because I want optional positional arguments
    # (that is, script [--test] [URL] [SCORE] [IS_NEW])
    test = url = score = is_new = None

    if "--test" in sys.argv:
        test = True
        sys.argv.remove("--test")
        logger.parent.setLevel(logging.DEBUG)

    if len(sys.argv) == 4 and sys.argv[3].casefold() in ["y", "n"]:
        is_new = sys.argv[3].casefold()

    if len(sys.argv) >= 3 and sys.argv[2] in ["1", "2", "3", "4", "5"]:
        score = int(sys.argv[2])

    if len(sys.argv) >= 2 and "https:" in sys.argv[1]:
        url = sys.argv[1]
    else:
        url = input("IMDb URL: ")
    url = url.strip().replace("/reference", "")

    while not score:
        _score = input("Rating (1-5): ").strip()
        if str(_score) in ("1", "2", "3", "4", "5"):
            score = str(_score)

    if not is_new:
        is_new = input("First viewing (y/N): ")
    first_viewing = is_new.strip().casefold() == "y"

    req = urllib.request.Request(
        "https://shell.fisher.one/imdb/",
        data=f"input={url}".encode("utf-8"),
        method="POST",
    )

    with urllib.request.urlopen(req) as _file:
        resp = _file.read().decode("utf-8")

    info = json.loads(resp)
    info["score"] = score
    info["first_viewing"] = first_viewing

    if test:
        print(info)
        print(make_entry(info))
    else:
        store(info)

        _title = urllib.parse.quote_plus(info["title"])
        subprocess.call(
            ["/usr/bin/open", f"https://letterboxd.com/search/{_title}/"]
        )
        subprocess.call(
            ["/usr/bin/open", f"https://trakt.tv/search?query={_title}"]
        )


if __name__ == "__main__":
    main()
