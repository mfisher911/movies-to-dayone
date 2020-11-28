#!/usr/bin/env python3

import logging
import sqlite3

# from https://docs.python.org/3/library/sqlite3.html
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def update(row):
    sql = "UPDATE movie SET summary = ?, imdb_url = ? WHERE id = ?"
    print(f"{row['title']}\n{row['imdb_url']}")
    imdb_url = input("IMDb URL: ")
    imdb_url = imdb_url.strip()
    summary = input("Summary: ")
    summary = summary.strip()

    do_update = imdb_url or summary

    if imdb_url:
        imdb_url = imdb_url.replace("reference", "")
    else:
        imdb_url = row["imdb_url"]

    if not summary:
        summary = "N/A"

    if do_update:
        cur = conn.cursor()
        cur.execute(
            sql,
            (
                summary,
                imdb_url,
                row["id"],
            ),
        )
        conn.commit()
        logging.debug("Updated %s", row["title"])
    else:
        logging.debug("No update for %s", row["title"])


def main():
    sql = "SELECT * FROM movie WHERE summary = 'N/A'"
    cursor = conn.cursor()
    cursor.execute(sql)
    for row in cursor.fetchall():
        update(row)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    conn = sqlite3.connect("movies.db")
    conn.row_factory = dict_factory

    main()

    conn.close()
