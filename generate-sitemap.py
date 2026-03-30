#!/usr/bin/env python3
"""
Generate sitemap.xml and slug-map.json from MyNewsdesk API articles + static pages.
slug-map.json maps article slugs to their IDs and types for client-side routing.
"""

import json
import os
import re
import ssl
import urllib.request
from datetime import datetime

API_KEY = "2J8377Ow95pCNFI_DPzZTQ"
BASE_URL = "https://www.mynewsdesk.com/services/pressroom"
SITE_URL = "https://newsroom.fomhochschule.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SITEMAP_FILE = os.path.join(SCRIPT_DIR, "sitemap.xml")
SLUGMAP_FILE = os.path.join(SCRIPT_DIR, "slug-map.json")

try:
    import certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_ctx = ssl.create_default_context()


def to_slug(title):
    """Convert title to URL slug (max 115 chars)."""
    slug = title.lower()
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in replacements.items():
        slug = slug.replace(k, v)
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    if len(slug) > 115:
        slug = slug[:115].rsplit("-", 1)[0]
    return slug


def fetch_articles(media_type, limit=100):
    """Fetch all articles of a given type with pagination."""
    all_items = []
    offset = 0

    while True:
        url = (
            f"{BASE_URL}/list/{API_KEY}"
            f"?format=json&type_of_media={media_type}"
            f"&limit={limit}&offset={offset}&strict=true"
        )
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, context=ssl_ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)
        offset += limit
        print(f"  Fetched {len(items)} {media_type}s (total: {len(all_items)})")

        if len(items) < limit:
            break

    return all_items


def generate():
    """Generate sitemap.xml and slug-map.json."""
    # Static pages
    static_pages = [
        {"loc": f"{SITE_URL}/", "changefreq": "daily", "priority": "1.0"},
        {"loc": f"{SITE_URL}/medien.html", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{SITE_URL}/kontakt.html", "changefreq": "monthly", "priority": "0.7"},
    ]

    # Fetch articles
    print("Fetching pressreleases...")
    pressreleases = fetch_articles("pressrelease")
    print("Fetching news...")
    news = fetch_articles("news")

    all_articles = []
    for item in pressreleases:
        item["_media_type"] = "pressrelease"
        all_articles.append(item)
    for item in news:
        item["_media_type"] = "news"
        all_articles.append(item)

    print(f"\nTotal articles: {len(all_articles)}")

    # Build slug map and sitemap
    slug_map = {}
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Static pages
    for page in static_pages:
        xml += "    <url>\n"
        xml += f"        <loc>{page['loc']}</loc>\n"
        xml += f"        <changefreq>{page['changefreq']}</changefreq>\n"
        xml += f"        <priority>{page['priority']}</priority>\n"
        xml += "    </url>\n"

    # Article pages
    seen_slugs = set()
    for item in all_articles:
        header = item.get("header", "")
        item_id = item.get("id", "")
        if not header or not item_id:
            continue

        slug = to_slug(header)
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        # Slug map entry
        slug_map[slug] = {"id": str(item_id), "type": item["_media_type"]}

        # Sitemap entry
        loc = f"{SITE_URL}/{slug}"

        updated = item.get("updated_at", {})
        lastmod = ""
        if isinstance(updated, dict) and updated.get("datetime"):
            lastmod = updated["datetime"][:10]
        elif isinstance(updated, str):
            lastmod = updated[:10]

        xml += "    <url>\n"
        xml += f"        <loc>{loc}</loc>\n"
        if lastmod:
            xml += f"        <lastmod>{lastmod}</lastmod>\n"
        xml += "        <changefreq>monthly</changefreq>\n"
        xml += "        <priority>0.6</priority>\n"
        xml += "    </url>\n"

    xml += "</urlset>\n"

    # Write sitemap
    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(xml)

    # Write slug map
    with open(SLUGMAP_FILE, "w", encoding="utf-8") as f:
        json.dump(slug_map, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\nSitemap written to {SITEMAP_FILE}")
    print(f"Slug map written to {SLUGMAP_FILE}")
    print(f"  Static pages: {len(static_pages)}")
    print(f"  Article pages: {len(seen_slugs)}")
    print(f"  Total URLs: {len(static_pages) + len(seen_slugs)}")


if __name__ == "__main__":
    generate()
