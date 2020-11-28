#!/usr/bin/env python3

import argparse
import csv
import logging
import os
import sqlite3

import httpx


def find_movie(title, year=None):
    """Search the DB for a movie title"""
    logging.debug("find_db_movie(%s, %s)", title, year)
    query = "SELECT * FROM movie WHERE title = ?"
    c = conn.cursor()
    c.execute(query, (title,))
    result = c.fetchone()

    if result:
        logging.info("Found %s (%s) in database", title, year)
    else:
        logging.info("Did not find %s (%s) in database", title, year)
        save_movie(find_imdb_movie(title, year))
        return find_movie(title, year)

    return result


def find_imdb_movie(title, year=None):
    """Search OMDb API for a movie title"""
    logging.debug("find_imdb_movie(%s, %s)", title, year)
    url = f"http://www.omdbapi.com/?apikey={APIKEY}&t={title}"
    params = {"apikey": APIKEY, "t": title}

    if year:
        params["y"] = year

    r = httpx.get(url, params=params)
    data = r.json()

    if data["Response"] == "True":
        data["imdb_url"] = f"https://www.imdb.com/title/{data['imdbID']}/"
    else:
        print(f"Could not find {title} ({year}) in OMDB.")
        if year:
            data["Year"] = year
        else:
            iyear = input("Year: ")
            data["Year"] = iyear.strip()
        url = input("IMDb URL: ")
        data["imdb_url"] = url.strip().replace("reference", "")
        summary = input("IMDb Summary: ")
        data["Plot"] = summary.strip()

    result = {
        "title": title,
        "year": data["Year"],
        "imdb_url": data["imdb_url"],
        "summary": data["Plot"],
    }

    logging.info("Found movie online: %s", result)

    return result


def save_movie(data):
    """Store info for a movie into the database"""
    logging.debug("save_movie(%s)", data)
    query = """
        INSERT INTO movie (title, year, imdb_url, summary) VALUES (?, ?, ?, ?)
    """

    c = conn.cursor()
    args = (
        data["title"],
        data["year"],
        data["imdb_url"],
        data["summary"],
    )
    c.execute(query, args)
    conn.commit()
    logging.debug(
        "save_movie(title=%s, year=%s, imdb_url=%s, summary)", *args
    )


def save_theater(data):
    """Store info for a theater into the database"""
    logging.debug("save_theater(%s)", data)
    query = """
        INSERT INTO theater (name, longitude, latitude) VALUES (?, ?, ?)
    """
    c = conn.cursor()
    args = (
        data["name"],
        data["longitude"],
        data["latitude"],
    )
    c.execute(query, args)
    conn.commit()
    logging.debug("save_theater(name=%s, longitude=%s, latitude=%s", *args)


def find_theater(theater):
    """Find a theater in the database or prompt user if it's not found"""
    logging.debug("find_theater(%s)", theater)
    query = "SELECT * FROM theater WHERE name = ?"
    c = conn.cursor()
    c.execute(query, (theater,))
    result = c.fetchone()
    logging.info("Found %s in database", theater)

    if not result:
        logging.info("Did not find %s in database", theater)
        print("Find theater in Google Maps...")
        longitude = None
        entry = input("Latitude: ")
        if ", " in entry:
            latitude, longitude = entry.split(",")
        else:
            latitude = entry

        if not longitude:
            longitude = input("Longitude: ")

        save_theater(
            {
                "name": theater,
                "latitude": latitude.strip(),
                "longitude": longitude.strip(),
            }
        )
        return find_theater(theater)

    return result


def save_entry(row):
    """Save a viewing (date, rating, new, movie ID, theater ID) in the DB"""
    logging.debug("save_entry(%s)", row)

    _ty = row["Title"]
    title = _ty[: (_ty.rfind("(") - 1)]
    year = _ty[(_ty.rfind("(") + 1) : (_ty.rfind(")"))]

    movie = find_movie(title=title, year=year)
    theater = find_theater(row["Theater"])

    new = 0
    if row["New"] == "N":
        new = 1

    query = """
        INSERT INTO viewing (movie, theater, date, score, first_viewing)
        VALUES (?, ?, ?, ?, ?);
    """

    # breakpoint()

    c = conn.cursor()
    args = (
        movie[0],
        theater[0],
        row["Date"],
        row["Score"],
        new,
    )

    c.execute(query, args)
    conn.commit()
    logging.debug(
        "saved(movie=%s, theater=%s, date=%s, score=%s, new=%s)", *args
    )


def initialize():
    """Code to build the database schema"""
    print("This will give errors if the database exists.")

    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE theater (
            id INTEGER PRIMARY KEY,
            name TEXT,
            longitude NUMERIC,
            latitude NUMERIC);
        """
    )
    conn.commit()

    c.execute(
        """
        CREATE TABLE movie (
            id INTEGER PRIMARY KEY,
            title TEXT,
            year TEXT,
            imdb_url TEXT,
            summary TEXT);
        """
    )
    conn.commit()

    c.execute(
        """
        CREATE TABLE viewing (
            id INTEGER PRIMARY KEY,
            movie INTEGER REFERENCES movie,
            theater INTEGER REFERENCES theater,
            date TEXT,
            score INTEGER,
            first_viewing INTEGER);
        """
    )
    conn.commit()


def main():
    """control function"""
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--initialize", action="store_true", help="initialize the database"
    )
    parser.add_argument(
        "--movies", action="store", help="list of movies (CSV)"
    )
    args = parser.parse_args()

    if args.initialize:
        initialize()
        logger.info("initialized the database.")

    elif args.movies:
        with open(args.movies) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                save_entry(row)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    APIKEY = os.getenv("OMDBAPIKEY")

    conn = sqlite3.connect("movies.db")

    main()

    conn.close()
