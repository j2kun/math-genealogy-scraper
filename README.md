# Math Genealogy

Code for scraping the math genealogy website.

A copy of the database, scraped on 2017-06-14, is contained in `data.json`.

Requirements:

 - python3.5+
 - aiohttp
 - beautifulsoup4

## Setup

Optionally create a virtualenvironment

```
virtualenv venv
source venv/bin/activate
```

Install required packages

```
pip install -r requirements.txt
```

Run it!

```
python fetch.py
```

The output, stored in `data.json`, is a dictionary with a single key `nodes`,
mapping to a list of dictionaries (specified by `parse.py`) of the form

```
{
  "students": [
    int, int, ...   <-- refers to the id field
  ],
  "advisors": [
    int, int, ...
  ],
  "name": str,
  "school": str,
  "subject": str,
  "thesis": str,
  "country": str,
  "year": int,
  "id": int,
}
```

Fields that were not found are null, or the empty list, as appropriate.

Example:

```
{
  "id": 186481,
  "name": "John Anthony Gerard Roberts",
  "thesis": "Order and Chaos in reversible Dynamical Systems",
  "school": "University of Melbourne",
  "country": "Australia",
  "year": 1990,
  "subject": null,
  "advisors": [
    53185,
    116308
  ],
  "students": [
    186482,
    186484,
    186486,
    186485
  ]
}
```

## Details

To be a nice person, this program rate-limits itself to have 5 concurrent
workers hitting the math genealogy website. Downloading the entire database in
this way takes about 6 hours. This repository contains a copy of the entire
dataset in `data.json` so you don't have to hammer their servers. This dataset
was fetched on 2017-06-14.

However, if you insist on being a bad person, you can increase the limit on the
worker semaphore in `fetch.py` and re-run it.

```
sem = asyncio.BoundedSemaphore(5)  # 5 workers
```
