# Notes:
import sys
import json
from pathlib import Path
from typing import Any

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

RT, OT = ReliabilityTypes, OriginTypes

PATH_HELPER = Path(__file__).parent
PATH_EVENT_GROUP = PATH_HELPER.parent
PATH_MEDIA = PATH_EVENT_GROUP / "media"


def retrieve_circles(event_name: str) -> list[Circle]:
    """Retrieve circles of given event. In the circle file has not been created, execute the creation script first."""
    circles_json_path = PATH_HELPER / event_name / "circles.json"
    if not circles_json_path.exists():
        print(
            f"Circle file for {event_name} not found, running the creation script ..."
        )
        creation_script_path = PATH_HELPER / event_name / "main.py"
        if not creation_script_path.exists():
            raise FileNotFoundError(
                f"Creation script for {event_name} not found at {creation_script_path}"
            )
        # Import main() from the creation script and execute
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            f"{event_name}.main", creation_script_path
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "main"):
                module.main()

        if not circles_json_path.exists():
            raise FileNotFoundError(
                f"Creation script {creation_script_path} failed to create {circles_json_path}"
            )

    with circles_json_path.open("r", encoding="utf-8") as f:
        circles_raw = json.load(f)
    return [Circle.load_from_json(c) for c in circles_raw]


if __name__ == "__main__":
    events: list[Event] = []
    active_events: list[int | str] = list(range(1, 4 + 1))

    i = 1  # ==== kagaocha1 ====
    if i in active_events:
        event_name = f"kagaocha{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "1_20160223054351_top.png",
                [
                    Source(
                        "https://web.archive.org/web/20160223054351/http://kagamine-no-ochakai.jp/index.html",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.01365, 135.7809429),
                address="9-1 Okazaki Seishojicho, Sakyo Ward, Kyoto, 606-8343, Japan",
                description="京都みやこめっせ 3F",
                sources=[
                    Source(
                        "Same as VOCALOID PARADISE 関西5 https://web.archive.org/web/20160223054351/http://kagamine-no-ochakai.jp/index.html",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWlur6oWztq77DaOuTZLw5MRyj3iDVD1CD-wl9_7wkEXC7e9JYhls5YX8XY6_936CE_RWP6CozLolZI73Mh7gleO-PgU9DJro4VpNaq7nQSPaHd9rChZ-VVge7urD47mbsVOMZ6B-A=s870-k-no",
                url="https://maps.app.goo.gl/8MjxYFEFKBxjhyTT8",
            ),
        ]
        event = Event(
            aliases=[
                "かがみねのお茶会",
                "Kagamine no Ocha Kai",
                "KagaOcha",
                "かがみね茶道部",
                "Kagamine Sadoubu",
            ],
            dates="2016.03.06",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://web.archive.org/web/20160223054351/http://kagamine-no-ochakai.jp/index.html",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20160426054358/http://kagamine-no-ochakai.jp:80/circle_list.html",
                    (RT.Reliable, OT.Official),
                ),
            ],
            locations=locations,
            description="Simultaneous with VOCALOID PARADISE 関西5.",
            comments="On twitter https://x.com/KagaOcha, one can get most circle images in higher quality. TODO perhaps.\nOn twitter, one can get images here https://web.archive.org/web/20160307153428/http://kagamine-no-ochakai.jp/plan/illust.html but without the watermarks.",
            last_edited="2026.08.05",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 2  # ==== kagaocha2 ====
    if i in active_events:
        event_name = f"kagaocha{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "2_20161024213452_top.png",
                [
                    Source(
                        "https://web.archive.org/web/20161024213452/http://kagamine-no-ochakai.jp/index.html",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            Medium(
                "2_20161024213452_kagaocha_logo.png",
                [
                    Source(
                        "https://web.archive.org/web/20161024213452/http://kagamine-no-ochakai.jp/index.html",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(35.01365, 135.7809429),
                address="9-1 Okazaki Seishojicho, Sakyo Ward, Kyoto, 606-8343, Japan",
                description="京都市勧業館みやこめっせ",
                sources=[
                    Source(
                        "Same as VOCALOID PARADISE 関西6 https://web.archive.org/web/20170308224328id_/http://kagamine-no-ochakai.jp:80/circle_list.html",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWlur6oWztq77DaOuTZLw5MRyj3iDVD1CD-wl9_7wkEXC7e9JYhls5YX8XY6_936CE_RWP6CozLolZI73Mh7gleO-PgU9DJro4VpNaq7nQSPaHd9rChZ-VVge7urD47mbsVOMZ6B-A=s870-k-no",
                url="https://maps.app.goo.gl/8MjxYFEFKBxjhyTT8",
            ),
        ]
        event = Event(
            aliases=[
                "かがみねのお茶会　二席目",
                "かがみねのお茶会2",
                "かがみね茶道部2",
                "Kagamine no Ocha Kai 2",
                "Kagamine Sadoubu 2",
            ],
            dates="2017.03.05",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://x.com/KagaOcha/status/706845107610210304",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20170308224328/http://kagamine-no-ochakai.jp:80/circle_list.html",
                    (RT.Reliable, OT.Official),
                ),
            ],
            locations=locations,
            description="Simultaneous with VOCALOID PARADISE 関西6, MUSIC COMMUNICATION 13, ボイスロイドマーチ, 結月家の食卓 おかえり and CeVIO FeSTA!!.",
            comments="On the official twitter https://x.com/KagaOcha, one may possibly find the circle catalog images for for this event. TODO perhaps.",
            last_edited="2026.08.05",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 3  # ==== kagaocha3 ====
    if i in active_events:
        event_name = f"kagaocha{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "3_20180316001802_top.png",
                [
                    Source(
                        "https://web.archive.org/web/20180316001802/http://kagamine-no-ochakai.jp/index.html",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(34.9473339, 135.7508794),
                address="5 Takeda Tobadonocho, Fushimi Ward, Kyoto, 612-8450, Japan",
                description="京都府総合見本市会館（京都パルスプラザ）",
                sources=[
                    Source(
                        "https://web.archive.org/web/20180406115110/http://kagamine-no-ochakai.jp/about.html",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWngwtW3CTY9qMFK-jYQVowY2JCJ97anQchzHm7zVLYykWkXyRICe7jgHhQQKCjg5VOWqXFI8MrvNRddGvWuXcKEwbjGUnKk1kM0_zo8KKdbr6xrIRZbPgJ9om65WepNsOvAkw0=s0?imgmax=0",
                url="https://maps.app.goo.gl/vC8pvtCnt3p9FR1dA",
            ),
        ]
        event = Event(
            aliases=[
                "かがみねのお茶会　三席目",
                "かがみねのお茶会3",
                "かがみね茶道部3",
                "Kagamine no Ocha Kai 3",
                "Kagamine Sadoubu 3",
            ],
            dates="2018.03.25",
            circles=[],
            media=media_,
            sources=[
                Source(
                    "Date: https://x.com/KagaOcha/status/932047234434084864",
                    (RT.Reliable, OT.Official),
                ),
                Source(
                    "Participating circles: https://web.archive.org/web/20180406083923/http://kagamine-no-ochakai.jp/circlelist.html",
                    (RT.Reliable, OT.Official),
                ),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.08.05",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    i = 4  # ==== kagaocha4 ====
    if i in active_events:
        event_name = f"kagaocha{i}"
        print(f"Processing {event_name} ...")

        media_ = [
            Medium(
                "4_20181201061034_top.png",
                [
                    Source(
                        "https://web.archive.org/web/20181201061034/http://kagamine-no-ochakai.jp/",
                        (RT.Reliable, OT.Official),
                    )
                ],
            ),
            # Medium("", [Source("", (RT.Reliable, OT.Official))]),
        ]
        locations = [
            Location(
                coordinates=(34.9473339, 135.7508794),
                address="5 Takeda Tobadonocho, Fushimi Ward, Kyoto, 612-8450, Japan",
                description="京都パルスプラザ(京都府総合見本市会館)",
                sources=[
                    Source(
                        "https://web.archive.org/web/20241107213415/http://kagamine-no-ochakai.jp/about.php",
                        (ReliabilityTypes.Reliable, OriginTypes.Official),
                    )
                ],
                # comments=None,
                imageUrl="https://lh3.googleusercontent.com/gps-cs-s/AHRPTWngwtW3CTY9qMFK-jYQVowY2JCJ97anQchzHm7zVLYykWkXyRICe7jgHhQQKCjg5VOWqXFI8MrvNRddGvWuXcKEwbjGUnKk1kM0_zo8KKdbr6xrIRZbPgJ9om65WepNsOvAkw0=s0?imgmax=0",
                url="https://maps.app.goo.gl/vC8pvtCnt3p9FR1dA",
            ),
        ]
        event = Event(
            aliases=[
                "かがみねのお茶会　四席目",
                "かがみねのお茶会4",
                "かがみね茶道部4",
                "Kagamine no ocha kai 4",
            ],
            dates="2019.01.27",
            circles=[],
            media=media_,
            sources=[
                Source("Date: https://x.com/KagaOcha/status/1018031533624516608", (RT.Reliable, OT.Official)),
                Source("Participating circles: https://web.archive.org/web/20210514174139/http://kagamine-no-ochakai.jp/circlelist.php", (RT.Reliable, OT.Official)),
            ],
            locations=locations,
            description=None,
            # comments=None,
            last_edited="2026.08.05",
        )

        # Retrieve circles
        event.circles = retrieve_circles(event_name)
        events.append(event)

    # i =   # ==== kagaocha ====
    # if i in active_events:
    #     event_name = f"kagaocha{i}"
    #     print(f"Processing {event_name} ...")

    #     media_ = [
    #         # Medium("", [Source("", (RT.Reliable, OT.Official))]),
    #         # Medium("", [Source("", (RT.Reliable, OT.Official))]),
    #         # Medium("", [Source("", (RT.Reliable, OT.Official))]),
    #     ]
    #     locations = [
    #         # Location(
    #         #     coordinates=(,),
    #         #     address="",
    #         #     description="",
    #         #     sources=[Source("", (ReliabilityTypes.Reliable, OriginTypes.Official))],
    #         #     # comments=None,
    #         #     imageUrl="",
    #         #     url="",
    #         # ),
    #     ]
    #     event = Event(
    #         aliases=,
    #         dates="",
    #         circles=[],
    #         media=media_,
    #         sources=[
    #             # Source(f"Date: {}", (RT.Reliable, OT.Official)),
    #             # Source("Participating circles: ", (RT.Reliable, OT.Official)),
    #         ],
    #         locations=locations,
    #         description=None,
    #         # comments=None,
    #         last_edited="2026.08.05",
    #     )

    #     # Retrieve circles
    #     # event.circles = retrieve_circles(event_name)
    #     events.append(event)

    # ==== event group ====
    media = [
        # Medium("",
        #        [Source("", (RT.Reliable, OT.Official))]),
        # Medium("",
        #        [Source("", (RT.Reliable, OT.Official))]),
    ]
    links = [
        "https://web.archive.org/web/20160223054351/http://kagamine-no-ochakai.jp/index.html",
        "https://x.com/KagaOcha",
        "http://com.nicovideo.jp/community/co2987729",
    ]

    event_group = EventGroup(
        aliases=[
            "かがみねのお茶会",
            "Kagamine no Ocha Kai",
            "KagaOcha",
            "かがみね茶道部",
            "Kagamine Sadoubu",
        ],
        events=events,
        media=media,
        links=links,
        sources=[
            Source(
                "Nickname 'かがみね茶道部': from copyright on the main website.",
                (ReliabilityTypes.Likely, OriginTypes.Official),
            )
        ],
        comments=None,
        description=None,
        last_edited="2026.08.05",
    )

    print(f"Saving {Path(__file__).stem} database...")
    event_group.save(PATH_EVENT_GROUP, indent=None)
    print("Done")
