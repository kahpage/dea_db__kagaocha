import sys
import json
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup
import lxml
import re

# Add project root to sys.path (find the directory containing db_structs.py)
_root = Path(__file__).resolve().parent
while _root.parent != _root:
    if (_root / "db_structs.py").exists():
        if str(_root) not in sys.path:
            sys.path.append(str(_root))
        break
    _root = _root.parent

from db_structs import (
    Medium,
    Circle,
    Event,
    EventGroup,
    Source,
    ReliabilityTypes,
    OriginTypes,
    Location,
)

PATH_EVENT = Path(__file__).parent
PATH_CIRCLES_JSON = PATH_EVENT / "circles.json"
NAME = PATH_EVENT.name


def retrieve_soup_fetch_if_needed(url: str) -> BeautifulSoup:
    """Retrieve BeautifulSoup object for the given URL, fetching the content if necessary."""
    html_path = PATH_EVENT / "raw.html"
    if not html_path.exists():
        print(f"Raw HTML file not found, fetching from {url} ...")
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve data from {url}, status code: {response.status_code}"
            )
        html_path.write_bytes(response.content)
    with html_path.open("rb") as f:
        return BeautifulSoup(f, "lxml")


def sanitize_string(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\s\n\t]+", " ", s)
    return s


def main():
    """Create circles.json"""
    print(f"Retrieving circles information for {NAME} ...")
    raw_url = "https://web.archive.org/web/20170308224328id_/http://kagamine-no-ochakai.jp:80/circle_list.html"
    
    # Parse the HTML content to extract circle information
    soup = retrieve_soup_fetch_if_needed(raw_url)
    circles = []

    # table: with border=1
    tables = soup.select('table')
    
    for table in tables:
        table_rows = table.select("tr")
        if not table_rows:
            raise Exception("No rows found in the circles table.")

        for row in table_rows:
                cols = row.select("td")
                if len(cols) < 7:
                    print("Skipping row with insufficient columns:", row)
                    continue

                circle_name = sanitize_string(cols[0].get_text())
                if "サークル名" in circle_name or not circle_name:
                    continue  # Skip header or empty rows
                
                pen_name = sanitize_string(cols[1].get_text())
                circle_urls: list[str] = []
                url_hp_tag = cols[2].select_one("a")
                if url_hp_tag and url_hp_tag.has_attr("href"):
                    circle_urls.append(url_hp_tag["href"])
                url_twitter_tag = cols[3].select_one("a")
                if url_twitter_tag and url_twitter_tag.has_attr("href"):
                    circle_urls.append(url_twitter_tag["href"])
                url_pixiv_tag = cols[4].select_one("a")
                if url_pixiv_tag and url_pixiv_tag.has_attr("href"):
                    circle_urls.append(url_pixiv_tag["href"])
                url_niconico_tag = cols[5].select_one("a")
                if url_niconico_tag and url_niconico_tag.has_attr("href"):
                    circle_urls.append(url_niconico_tag["href"])

                position = sanitize_string(cols[6].get_text())

                circle = Circle(
                    aliases=[circle_name],
                    pen_names=[pen_name] if pen_name else None,
                    links=[circle_urls] if circle_urls else None,
                    position=position,
                    # comments=", ".join(comment_parts) if comment_parts else None,
                )

                circles.append(circle)

    # Save the extracted circle information to a JSON file
    with open(PATH_CIRCLES_JSON, "w", encoding="utf-8") as f:
        json.dump([c.get_json() for c in circles], f, ensure_ascii=False, indent=2)
    print(f"Saved {len(circles)} circles to {PATH_CIRCLES_JSON}")


if __name__ == "__main__":
    main()
