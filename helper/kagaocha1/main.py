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
PATH_EVENT_GROUP = PATH_EVENT.parent.parent
PATH_MEDIA = PATH_EVENT_GROUP / "media"
PATH_CUTS = PATH_MEDIA / "01_cuts"
if not PATH_CUTS.exists():
    PATH_CUTS.mkdir(parents=True, exist_ok=True)

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

def download_if_not_exists(url: str, save_path: Path) -> None:
    """Download the file from the given URL if it does not already exist at the save_path."""
    if not save_path.exists():
        print(f"Downloading {url} to {save_path} ...")
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to download {url}, status code: {response.status_code}"
            )
        save_path.write_bytes(response.content)

def sanitize_string(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\s\n\t]+", " ", s)
    return s


def main():
    """Create circles.json"""
    print(f"Retrieving circles information for {NAME} ...")
    raw_url = "https://web.archive.org/web/20160426054358fw_/http://kagamine-no-ochakai.jp:80/circle_list.html"
    
    # Parse the HTML content to extract circle information
    soup = retrieve_soup_fetch_if_needed(raw_url)
    circles = []

    # table: with border=1
    # div class="circle_list"
    circle_list_tag = soup.find("div", class_="circle_list")
    if not circle_list_tag:
        raise ValueError("Could not find the circle list in the HTML content.")
    
    circle_divs = circle_list_tag.find_all("div", class_="dat")

    for i, circle_div in enumerate(circle_divs):
        # Tag name, of the form POSITION<br/>CIRCLE_NAME
        tag_name = circle_div.find("div", class_="name")
        if not tag_name:
            print(f"Warning: Could not find name tag for circle {i}")
        name_parts = tag_name.decode_contents().split("<br/>")
        if len(name_parts) != 2:
            print(f"Warning: Unexpected name format for circle {i}: {tag_name.decode_contents()}")
            continue
        position = sanitize_string(name_parts[0].replace("配置：", ""))
        circle_name = sanitize_string(name_parts[1].replace("サークル名：", ""))

        # p class="toolTip"
        tooltip_tag = circle_div.find("p", class_="toolTip")
        if not tooltip_tag:
            print(f"Warning: Could not find tooltip tag for circle {i} ({circle_name})")
            continue

        comments_parts: list[str] = []
        tooltip_description = sanitize_string(tooltip_tag.get_text(strip=True).replace("♪サークルPR", ""))
        if tooltip_description:
            comments_parts.append(tooltip_description)
        else:
            print(f"Warning: Tooltip description is empty for circle {i} ({circle_name})")

        cut_url_tag = circle_div.find("img", class_="toolTip")
        if not cut_url_tag or not cut_url_tag.get("src"):
            print(f"Warning: Could not find cut image tag for circle {i} ({circle_name})")
            continue
        cut_url = f"https://web.archive.org{cut_url_tag['src']}"

        # div class="pr"
        pr_tag = circle_div.find("div", class_="pr")
        if not pr_tag:
            print(f"Warning: Could not find pr tag for circle {i} ({circle_name})")
            continue
        pen_name = sanitize_string(pr_tag.get_text(strip=True).replace("ペンネーム：", ""))

        # div class="info"
        info_tag = circle_div.find("div", class_="info")
        if not info_tag:
            print(f"Warning: Could not find info tag for circle {i} ({circle_name})")
            continue
        info_table = info_tag.find("table")
        if not info_table:
            print(f"Warning: Could not find info table for circle {i} ({circle_name})")
            continue
        circle_urls: list[str] = []
        for col in info_table.find_all("td"):
            if col_content := col.find("a"):
                circle_urls.append(sanitize_string(col_content["href"].replace("https://web.archive.org/web/20160426054358/", "")))

        media: list[Medium] = []
        if cut_url:
            _name = sanitize_string(Path(cut_url).name)
            cut_save_path = PATH_CUTS / _name
            download_if_not_exists(cut_url, cut_save_path)
            media.append(Medium(f"01_cuts/{_name}", [Source(cut_url, (ReliabilityTypes.Reliable, OriginTypes.Official))]))

        circle = Circle(
            aliases=[circle_name],
            pen_names=[pen_name] if pen_name else None,
            links=circle_urls if circle_urls else None,
            position=position,
            comments=", ".join(comments_parts) if comments_parts else None,
            media=media if media else None
        )

        circles.append(circle)

    # Save the extracted circle information to a JSON file
    with open(PATH_CIRCLES_JSON, "w", encoding="utf-8") as f:
        json.dump([c.get_json() for c in circles], f, ensure_ascii=False, indent=2)
    print(f"Saved {len(circles)} circles to {PATH_CIRCLES_JSON}")


if __name__ == "__main__":
    main()
