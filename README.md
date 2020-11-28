# Movies to DayOne

Problem: from 2003 to 2014, I kept track of movies I watched in an
OrgMode file. By 2014, I wanted to do this with a more mobile-first
approach, so I started tracking them in the [Day
One](https://dayoneapp.com) journal (which ended up getting a template
managed by an iOS Workflow/Shortcut).

I captured the following attributes:

- Date Watched
- Title -- as shown by IMDb, for instance: 28 Days Later... (2002)
- Where -- viewing location (theater name or perhaps media, like
  "VHS")
- Score -- integer rating, 1-5
- New -- Boolean -- was this first time I saw it?

When I translated this to DayOne, I wanted to expand to match the
current Day One entry template, which is something like this:

    28 Days Later... (2002)   # title
    5/5                       # rating
    IMDb summary
    -- IMDb link

In Day One, I use tags for easier filtering: this entry would be
tagged "5/5" and "Movies". If it was a first viewing, it also would be
tagged "new".

## Data (cleaning) Requirements

I wanted to look up the IMDb summaries and URLs based on the titles. I
found a web service, the [OMDb API](http://www.omdbapi.com), that made
this substantially easier, although not perfect.

Day One can also store the geographic coordinates of the entry
location. Since I had theater names, I wanted to find them (where
possible: some theaters closed since I went).

I converted the Org Mode file to a CSV and walked through the data,
looking up the IMDb and location information as I went. I stored the
results in a SQLite database, with `movies_to_db.py`.

## Outcome

I had roughly 1,300 entries in the Org Mode file (not all were
unique), but the OMDb API limited free use to 1,000 queries a day, so
I did my lookups over a weekend.

If a movie has a non-English original name, I like to store that.
There were several instances where a title I stored (via copy/paste
from IMDb into the file) couldn't be found. I could generally find the
titles by doing other web searches and then find the IMDb pages.

There were also a handful of movies where the title search I did
through OMDb API yielded a documentary segment about the movie instead
of the actual movie, so I had to do some manual cleanup
(`clean_db.py`).

Finally, I loaded the historic entries into a new Day One journal,
using `db_to_dayone.py`. After that, I was frequently able to use the
Day One map tool to zoom to the specific theater locations and add
back in theater names, using Day One's affiliation with Foursquare.

## Regrets

I should have been more careful to write out HTTPS URLs in the journal
entries with `movies_to_db.py`. I must have looked at an old entry
instead of a current one when I was building the template, and I
didn't notice this until too late.
