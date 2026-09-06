#!/usr/bin/env python3
"""
Build an Applied Linguistics CFP RSS feed.

Sources:
- LINGUIST List Calls RSS
- AILA website pages (WordPress RSS)
The filter keeps items whose title/summary/content contains applied-linguistics
keywords, while allowing broad ELT/TESOL/CALL/assessment/etc. CFPs.
"""

from __future__ import annotations
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

OUT = Path("docs/feed.xml")
MAX_ITEMS = 100

SOURCES = [
    ("LINGUIST List — Calls", "https://linguistlist.org/issues/rss/calls"),
    ("AILA", "https://aila.info/feed/"),
]

# Adjust this list to make the feed narrower or broader.
KEYWORDS = [
    "applied linguistics", "applied language", "language education",
    "language teaching", "language learning", "second language",
    "foreign language", "additional language", "multilingual", "plurilingual",
    "translanguaging", "tesol", "elt", "english language teaching",
    "esl", "efl", "call", "corpus linguistics", "learner corpus",
    "language assessment", "language testing", "sociolinguistics",
    "discourse analysis", "pragmatics", "psycholinguistics",
    "computer-assisted language learning", "call", "technology-enhanced",
    "ai", "translation", "interpreting", "academic writing",
    "literacies", "teacher education", "language policy",
]

CFP_MARKERS = [
    "call for papers", "call for proposals", "call for abstracts",
    "cfp", "submission deadline", "proposals are invited",
    "abstract submission", "papers are invited",
]

def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Applied-Linguistics-CFP-RSS/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return html.unescape(re.sub(r"\s+", " ", s)).strip()

def text_of(el):
    return " ".join(el.itertext()).strip() if el is not None else ""

def parse_feed(source_name: str, data: bytes):
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item"):
        title = text_of(item.find("title"))
        link = text_of(item.find("link"))
        desc = text_of(item.find("description"))
        pub = text_of(item.find("pubDate"))
        guid = text_of(item.find("guid")) or link
        blob = f"{title} {desc}".lower()

        # Require a CFP signal, then require an applied-linguistics signal.
        if not any(k in blob for k in CFP_MARKERS):
            # LINGUIST List's Calls feed is already CFP-focused.
            if source_name != "LINGUIST List — Calls":
                continue
        if not any(k in blob for k in KEYWORDS):
            continue

        items.append({
            "title": title,
            "link": link,
            "description": strip_html(desc),
            "pubDate": pub,
            "guid": f"{source_name}:{guid}",
        })
    return items

def parse_date(s):
    try:
        from email.utils import parsedate_to_datetime
        d = parsedate_to_datetime(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

def build():
    all_items = []
    for source, url in SOURCES:
        try:
            all_items.extend(parse_feed(source, fetch(url)))
        except Exception as e:
            print(f"Warning: {source} unavailable: {e}")

    # Deduplicate by URL/title and keep newest.
    seen = set()
    unique = []
    for x in sorted(all_items, key=lambda x: parse_date(x["pubDate"]), reverse=True):
        key = x["link"] or x["title"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(x)

    unique = unique[:MAX_ITEMS]
    OUT.parent.mkdir(parents=True, exist_ok=True)

    rss = ET.Element("rss", {"version": "2.0"})
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = "Applied Linguistics — Calls for Papers"
    ET.SubElement(ch, "link").text = "https://YOUR-USERNAME.github.io/YOUR-REPO/feed.xml"
    ET.SubElement(ch, "description").text = (
        "Automatically filtered calls for papers, calls for abstracts, "
        "and related publication opportunities in applied linguistics."
    )
    ET.SubElement(ch, "language").text = "en"
    ET.SubElement(ch, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
    ET.SubElement(ch, "ttl").text = "1440"

    for x in unique:
        item = ET.SubElement(ch, "item")
        ET.SubElement(item, "title").text = x["title"]
        ET.SubElement(item, "link").text = x["link"]
        ET.SubElement(item, "description").text = x["description"][:5000]
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = x["guid"]
        if x["pubDate"]:
            ET.SubElement(item, "pubDate").text = x["pubDate"]

    ET.indent(rss, space="  ")
    OUT.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(rss, encoding="unicode"),
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(unique)} items.")

if __name__ == "__main__":
    build()
