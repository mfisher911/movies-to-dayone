#!/usr/bin/env python3

import logging
import sqlite3
import subprocess
import time


# from https://docs.python.org/3/library/sqlite3.html
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_full_movie_list():
    sql = """
        SELECT m.title, m.year, m.imdb_url, m.summary, v.date,
               v.score, v.first_viewing, t.name,
               t.longitude, t.latitude
        FROM viewing v, movie m, theater t
        WHERE v.movie = m.id AND v.theater = t.id
        ORDER BY v.id
"""
    cursor = conn.cursor()
    cursor.execute(sql)
    for row in cursor.fetchall():
        yield row


def output(row):
    coordinates = None
    args = [
        "dayone2",
        "--journal",
        "movies",
        "--time-zone",
        "America/New_York",
    ]
    if row["summary"] == "N/A":
        summary = "\n"
    else:
        summary = f"\n{row['summary']}"
    rating = f"{row['score']}/5"
    entry = (
        f"# {row['title']} ({row['year']})\n{rating}\n{summary}\n"
        f"-- {row['imdb_url']}"
    )

    outdate = ["--date", row["date"]]
    tags = ["--tags", "OMDB", "Movies", rating]
    if row["first_viewing"]:
        tags.append("new")

    if row["latitude"]:
        coordinates = [
            "--coordinate",
            str(row["latitude"]),
            str(row["longitude"]),
        ]

    if coordinates:
        args.extend(coordinates)
    args.extend(outdate)
    args.extend(tags)
    args.extend(["--", "new"])

    subprocess.run(
        args=args, input=entry, check=True, capture_output=True, text=True
    )
    logger.debug("STDOUT: %s\nargs: %s", entry, " ".join(args))
    time.sleep(5)


def main():
    movies = get_full_movie_list()
    for movie in movies:
        output(movie)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    conn = sqlite3.connect("movies.db")
    conn.row_factory = dict_factory

    main()

    conn.close()
