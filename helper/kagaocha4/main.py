import sys
import json
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup
import lxml
from urllib.parse import urljoin
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
    raw_url = "https://web.archive.org/web/20210514174139id_/http://kagamine-no-ochakai.jp/circlelist.php"
    
    # Parse the HTML content to extract circle information
    soup = retrieve_soup_fetch_if_needed(raw_url)
    circles = []

    # table: with border=1
    tables = soup.select('table')
    
    for table in tables:
        table_rows = table.select("tr")
        if not table_rows:
            raise Exception("No rows found in the circles table.")

        # helper to extract links from a cell
        def extract_links_from_cell(cell, base_url: str) -> list[str]:
            links: list[str] = []
            for a in cell.find_all("a"):
                href = a.get("href")
                if not href:
                    continue
                href = urljoin(base_url, href)
                if href.startswith("javascript:"):
                    continue
                links.append(href)
            for u in re.findall(r'https?://[^\s<>"\)]+', cell.get_text()):
                if u not in links:
                    links.append(u)
            return links

        current = None
        for row in table_rows:
            cols = row.select("td")
            # Determine whether this row starts a new circle.
            # Starter rows usually have the position in the first cell and often a rowspan,
            # or they contain many columns. Continuation rows (additional link rows)
            # commonly have a single cell with a link.
            first_text = cols[0].get_text(strip=True) if cols else ""
            is_rowspan = bool(cols and cols[0].has_attr("rowspan"))
            is_wide = len(cols) >= 7
            if (is_rowspan or is_wide) and first_text and "配置" not in first_text:
                # finalize previous circle
                if current:
                    # dedupe urls
                    seen = set()
                    deduped = []
                    for u in current["urls"]:
                        if u not in seen:
                            seen.add(u)
                            deduped.append(u)
                    current["urls"] = deduped
                    # build Circle object
                    circle = Circle(
                        aliases=[current["name"]],
                        pen_names=[current["pen"]] if current.get("pen") else None,
                        links=current["urls"] if current["urls"] else None,
                        position=current["position"],
                        comments=current.get("comments") if current.get("comments") else None,
                    )
                    circles.append(circle)

                # start new current circle
                position = sanitize_string(cols[0].get_text())
                if not position:
                    current = None
                    continue
                circle_name = sanitize_string(cols[1].get_text()) if len(cols) > 1 else ""
                pen_name = sanitize_string(cols[2].get_text()) if len(cols) > 2 else ""
                description = sanitize_string(cols[7].get_text()) if len(cols) > 7 else ""
                current = {"position": position, "name": circle_name, "pen": pen_name, "urls": [], "comments": description}

                # extract links from this starter row (columns 3..6)
                for col_idx in (3, 4, 5, 6):
                    if col_idx < len(cols):
                        try:
                            current["urls"].extend(extract_links_from_cell(cols[col_idx], raw_url))
                        except Exception as exc:
                            # continue but don't crash
                            continue
            else:
                # continuation row for the current circle: collect any links present
                if not current:
                    continue
                for col in cols:
                    try:
                        current["urls"].extend(extract_links_from_cell(col, raw_url))
                    except Exception:
                        continue

        # after looping rows, finalize last circle
        if current:
            seen = set()
            deduped = []
            for u in current["urls"]:
                if u not in seen:
                    seen.add(u)
                    deduped.append(u)
            current["urls"] = deduped
            circle = Circle(
                aliases=[current["name"]],
                pen_names=[current["pen"]] if current.get("pen") else None,
                links=current["urls"] if current["urls"] else None,
                position=current["position"],
                comments=current.get("comments") if current.get("comments") else None,
            )
            circles.append(circle)

    # Save the extracted circle information to a JSON file
    with open(PATH_CIRCLES_JSON, "w", encoding="utf-8") as f:
        json.dump([c.get_json() for c in circles], f, ensure_ascii=False, indent=2)
    print(f"Saved {len(circles)} circles to {PATH_CIRCLES_JSON}")


if __name__ == "__main__":
    main()
