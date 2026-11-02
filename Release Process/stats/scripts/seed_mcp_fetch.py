#!/usr/bin/env python3
"""Seed mcp_import/_fetch/{version}/ with execution_meta.json and cloud.json from manifest MCP gather."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FETCH = ROOT / "Release Process" / "stats" / "mcp_import" / "_fetch"
SITE = "https://appfire.atlassian.net"

# Execution + cloud snapshots from plugin-atlassian-atlassian (2026-10-28).
SEED: dict[str, dict] = {
    "8.62": {
        "execution": {
            "summary": "BigPicture 8.62 Major Release Test Run Jira Cloud Manual",
            "status": "Done",
            "created": "2025-10-16T06:01:27.330-0400",
            "url": f"{SITE}/browse/TC-5779",
            "defect_keys": [
                "ONE-157948",
                "ONE-158983",
                "ODEV-3052",
                "ONE-158993",
                "ONE-119684",
                "ONE-158997",
                "ONE-160310",
                "ONE-160322",
            ],
        },
        "cloud": {
            "values": [
                {"id": "33478", "name": "bigpicture-cloud-8.62.0.0", "released": False, "releaseDate": None},
                {"id": "33627", "name": "bigpicture-cloud-8.62.0.1", "released": False, "releaseDate": None},
                {
                    "id": "33652",
                    "name": "bigpicture-cloud-8.62.0.2",
                    "released": True,
                    "releaseDate": "2025-10-30",
                },
            ]
        },
    },
    "8.63": {
        "execution": {
            "summary": "BigPicture 8.63 Major Release Test Run Jira Cloud Manual",
            "status": "Done",
            "created": "2025-10-30T05:59:01.002-0400",
            "url": f"{SITE}/browse/TC-5808",
            "defect_keys": ["ONE-222308", "ONE-173221", "ONE-165845", "ONE-174464"],
        },
        "cloud": {
            "values": [
                {"id": "33738", "name": "bigpicture-cloud-8.63.0.0", "released": False, "releaseDate": None},
                {
                    "id": "35033",
                    "name": "bigpicture-cloud-8.63.0.1",
                    "released": True,
                    "releaseDate": "2025-11-19",
                },
            ]
        },
    },
    "8.64": {
        "execution": {
            "summary": "BigPicture 8.64 Major Release Test Run Jira Cloud Manual",
            "status": "Done",
            "created": "2025-11-14T06:05:01.838-0500",
            "url": f"{SITE}/browse/TC-5818",
            "defect_keys": [
                "ONE-187629",
                "ONE-214988",
                "ONE-188911",
                "ONE-165845",
                "ONE-188919",
                "ONE-188922",
                "ONE-188925",
                "ONE-188926",
                "ONE-188931",
                "ONE-188933",
                "ONE-190236",
                "ONE-190237",
                "ONE-190240",
                "ONE-188905",
            ],
        },
        "cloud": {
            "values": [
                {"id": "36064", "name": "bigpicture-cloud-8.64.0.5", "released": False, "releaseDate": None},
                {"id": "36068", "name": "bigpicture-cloud-8.64.0.6", "released": False, "releaseDate": None},
                {
                    "id": "36347",
                    "name": "bigpicture-cloud-8.64.0.7",
                    "released": True,
                    "releaseDate": "2025-12-08",
                },
            ]
        },
    },
    "8.65": {
        "execution": {
            "summary": "BigPicture 8.65 Major Release Test Run Jira Cloud Manual",
            "status": "In Progress",
            "created": "2025-12-08T04:08:59.550-0500",
            "url": f"{SITE}/browse/TC-5841",
            "defect_keys": [
                "ONE-204996",
                "ONE-205001",
                "ONE-204991",
                "ONE-206344",
                "ONE-206354",
                "ONE-206908",
            ],
        },
        "cloud": {
            "values": [
                {"id": "36370", "name": "bigpicture-cloud-8.65.0.0", "released": False, "releaseDate": None},
                {"id": "36841", "name": "bigpicture-cloud-8.65.0.1", "released": False, "releaseDate": None},
                {
                    "id": "36942",
                    "name": "bigpicture-cloud-8.65.0.2",
                    "released": True,
                    "releaseDate": "2025-12-29",
                },
            ]
        },
    },
    "8.66": {
        "execution": {
            "summary": "BigPicture 8.66 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-01-02T03:08:08.891-0500",
            "url": f"{SITE}/browse/TC-5907",
            "defect_keys": [
                "ONE-208075",
                "ONE-206354",
                "ONE-208507",
                "ONE-208083",
                "ONE-208511",
                "ODEV-3172",
                "ONE-208509",
                "ONE-208512",
                "ONE-208514",
                "ONE-208604",
                "ONE-165845",
            ],
        },
        "cloud": {
            "values": [
                {"id": "37590", "name": "bigpicture-cloud-8.66.0.0", "released": False, "releaseDate": None},
                {"id": "37640", "name": "bigpicture-cloud-8.66.0.1", "released": False, "releaseDate": None},
                {"id": "38204", "name": "bigpicture-cloud-8.66.0.2", "released": False, "releaseDate": None},
                {
                    "id": "39250",
                    "name": "bigpicture-cloud-8.66.0.3",
                    "released": True,
                    "releaseDate": "2026-01-29",
                },
            ]
        },
    },
    "8.67": {
        "execution": {
            "summary": "BigPicture 8.67 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-01-28T08:33:06.259-0500",
            "url": f"{SITE}/browse/TC-5960",
            "defect_keys": ["ONE-212944"],
        },
        "cloud": {
            "values": [
                {"id": "39494", "name": "bigpicture-cloud-8.67.0.0", "released": False, "releaseDate": None},
                {
                    "id": "40829",
                    "name": "bigpicture-cloud-8.67.0.1",
                    "released": True,
                    "releaseDate": "2026-02-11",
                },
            ]
        },
    },
    "8.68": {
        "execution": {
            "summary": "BigPicture 8.68 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-02-11T10:14:01.743-0500",
            "url": f"{SITE}/browse/TC-5984",
            "defect_keys": [
                "ONE-223862",
                "ONE-224633",
                "ONE-224654",
                "ONE-224655",
                "ONE-224658",
                "ONE-224662",
                "ONE-224672",
                "ONE-225578",
                "ONE-225588",
                "ONE-225582",
                "ONE-226390",
                "ONE-226393",
                "ONE-226401",
            ],
        },
        "cloud": {
            "values": [
                {"id": "41650", "name": "bigpicture-cloud-8.68.0.0", "released": False, "releaseDate": None},
                {"id": "42820", "name": "bigpicture-cloud-8.68.0.1", "released": False, "releaseDate": None},
                {"id": "43029", "name": "bigpicture-cloud-8.68.0.2", "released": False, "releaseDate": None},
                {"id": "43066", "name": "bigpicture-cloud-8.68.0.3", "released": False, "releaseDate": None},
            ]
        },
    },
    "8.69": {
        "execution": {
            "summary": "BigPicture 8.69 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-02-24T01:57:56.502-0500",
            "url": f"{SITE}/browse/TC-5987",
            "defect_keys": [
                "ONE-230357",
                "ONE-230360",
                "ONE-206908",
                "ONE-230363",
                "ONE-230365",
                "ONE-230368",
                "ONE-206354",
                "ONE-230369",
                "ONE-230376",
                "ONE-230957",
                "ONE-230959",
            ],
        },
        "cloud": {
            "values": [
                {"id": "43591", "name": "bigpicture-cloud-8.69.0.0", "released": False, "releaseDate": None},
                {"id": "44649", "name": "bigpicture-cloud-8.69.0.1", "released": False, "releaseDate": None},
                {"id": "44658", "name": "bigpicture-cloud-8.69.0.2", "released": False, "releaseDate": None},
                {"id": "45074", "name": "bigpicture-cloud-8.69.0.3", "released": False, "releaseDate": None},
                {"id": "45669", "name": "bigpicture-cloud-8.69.1.0", "released": False, "releaseDate": None},
            ]
        },
    },
    "8.70": {
        "execution": {
            "summary": "BigPicture 8.70 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-03-17T04:51:40.841-0400",
            "url": f"{SITE}/browse/TC-6028",
            "defect_keys": [
                "ONE-241988",
                "ONE-241990",
                "ONE-243032",
                "ONE-243027",
                "ONE-243037",
                "ONE-243048",
                "ONE-206908",
                "ONE-244059",
            ],
        },
        "cloud": {
            "values": [
                {"id": "45900", "name": "bigpicture-cloud-8.70.0.0", "released": False, "releaseDate": None},
                {"id": "46103", "name": "bigpicture-cloud-8.70.0.1", "released": False, "releaseDate": None},
                {"id": "46476", "name": "bigpicture-cloud-8.70.0.2", "released": False, "releaseDate": None},
                {"id": "46780", "name": "bigpicture-cloud-8.70.0.3", "released": False, "releaseDate": None},
                {"id": "46816", "name": "bigpicture-cloud-8.70.0.4", "released": False, "releaseDate": None},
                {"id": "46820", "name": "bigpicture-cloud-8.70.0.5", "released": False, "releaseDate": None},
                {"id": "46889", "name": "bigpicture-cloud-8.70.0.6", "released": False, "releaseDate": None},
                {
                    "id": "46960",
                    "name": "bigpicture-cloud-8.70.0.7",
                    "released": True,
                    "releaseDate": "2026-05-18",
                },
                {
                    "id": "49154",
                    "name": "bigpicture-cloud-8.70.1.0",
                    "released": True,
                    "releaseDate": "2026-05-18",
                },
            ]
        },
    },
    "8.71": {
        "execution": {
            "summary": "BigPicture 8.71 Major Release Test Run Automated",
            "status": "To Do",
            "created": "2026-04-10T09:04:29.193-0400",
            "url": f"{SITE}/browse/TC-6045",
            "defect_keys": [],
        },
        "cloud": {
            "values": [
                {"id": "49714", "name": "bigpicture-cloud-8.71.0.0", "released": False, "releaseDate": None},
                {
                    "id": "51120",
                    "name": "bigpicture-cloud-8.71.0.1",
                    "released": True,
                    "releaseDate": "2026-05-18",
                },
            ]
        },
    },
    "8.72": {
        "execution": {
            "summary": "BigPicture 8.72 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-05-15T06:47:28.737-0400",
            "url": f"{SITE}/browse/TC-6177",
            "defect_keys": [
                "ONE-206908",
                "ONE-315335",
                "ONE-315337",
                "ONE-315341",
                "ONE-317200",
                "ONE-317201",
                "ONE-317206",
            ],
        },
        "cloud": {
            "values": [
                {"id": "52488", "name": "bigpicture-cloud-8.72.0.0", "released": False, "releaseDate": None},
                {
                    "id": "53272",
                    "name": "bigpicture-cloud-8.72.0.2",
                    "released": False,
                    "releaseDate": "2026-06-15",
                },
            ]
        },
    },
    "8.73": {
        "execution": {
            "summary": "BigPicture 8.73 Major Release Test Run Jira Cloud Manual",
            "status": "To Do",
            "created": "2026-06-15T06:34:49.338-0400",
            "url": f"{SITE}/browse/TC-6300",
            "defect_keys": [
                "ONE-333687",
                "ONE-333868",
                "ONE-334609",
                "ONE-334619",
                "ONE-335534",
                "ONE-335558",
            ],
        },
        "cloud": {
            "values": [
                {
                    "id": "54718",
                    "name": "bigpicture-cloud-8.73.0.1",
                    "released": False,
                    "releaseDate": "2026-07-13",
                },
                {
                    "id": "54795",
                    "name": "bigpicture-cloud-8.73.0.2",
                    "released": True,
                    "releaseDate": "2026-07-20",
                },
            ]
        },
    },
}


def main() -> None:
    for version, data in SEED.items():
        d = FETCH / version
        d.mkdir(parents=True, exist_ok=True)
        (d / "execution_meta.json").write_text(
            json.dumps(data["execution"], indent=2, ensure_ascii=False) + "\n"
        )
        (d / "cloud.json").write_text(
            json.dumps({"data": data["cloud"]}, indent=2, ensure_ascii=False) + "\n"
        )
        if not (d / "bugs.json").is_file() and not (d / "bugs_merged.json").is_file():
            (d / "bugs.json").write_text('{"issues":[]}\n')
    print(f"seeded {len(SEED)} versions under {FETCH}")


if __name__ == "__main__":
    main()
