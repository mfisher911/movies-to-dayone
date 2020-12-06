#!/usr/bin/env python3

import json
import logging
import urllib.request
import subprocess


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
        tags.append("first_viewing")

    args.extend(tags)
    args.extend(["--", "new"])

    logger.debug("STDOUT: %s\nargs: %s", entry, " ".join(args))
    subprocess.run(
        args=args, input=entry, check=True, capture_output=True, text=True
    )
    subprocess.call(["/usr/bin/open", "/Applications/Day One.app"])


def main():
    """Get user input and store the info to DayOne"""
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
    print(f"<https://letterboxd.com/search/{info['letterboxd_title']}/>")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger()
    main()