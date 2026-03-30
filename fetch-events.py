#!/usr/bin/env python3
"""
Fetch future published events from Microsoft Dynamics 365 and output as JSON.
Uses only urllib and certifi (no pip dependencies beyond certifi).

Constructs correct image URLs from _msevtmgt_eventimage_value lookup ID,
since msevtmgt_eventimageurl often points to the wrong image.
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ── Dynamics 365 credentials ──
ORG_URL = "https://bcw-gruppe.crm4.dynamics.com"
CLIENT_ID = "affd8c64-dac7-44a3-9d1c-2ffc52f63205"
CLIENT_SECRET = "oVZ8Q~_MMX_V_iOf_-BjZSiEmAq8s6sof33YYaOv"
TENANT_ID = "25341995-fa74-43de-8fbf-e48ba0e30a0b"

# Dynamics Marketing assets base URL (org-specific)
ASSETS_BASE = "https://assets-eur.mkt.dynamics.com/9e1171ae-57ef-4ed6-a5f4-e1e95b1d527a/digitalassets/images"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "events.json")

# ── SSL context using certifi ──
try:
    import certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_ctx = ssl.create_default_context()


def get_access_token():
    """Authenticate via OAuth2 client credentials flow."""
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": f"{ORG_URL}/.default"
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["access_token"]


def strip_html(text):
    """Remove HTML tags from a string."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = clean.replace("&nbsp;", " ").replace("&amp;", "&")
    clean = clean.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    # Preserve line breaks for bullet points
    clean = re.sub(r"\n\s*\n", "\n", clean)
    clean = re.sub(r"[ \t]+", " ", clean).strip()
    return clean


def fetch_events(token):
    """Fetch all future published events with pagination."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

    select_fields = ",".join([
        "msevtmgt_name",
        "msevtmgt_eventstartdate",
        "msevtmgt_eventenddate",
        "msevtmgt_description",
        "msevtmgt_eventformat",
        "msevtmgt_eventtype",
        "msevtmgt_maximumeventcapacity",
        "msevtmgt_registrationcount",
        "msevtmgt_checkincount",
        "msevtmgt_eventimageurl",
        "msevtmgt_publiceventurl",
        "msevtmgt_publishstatus",
        "bcw_art_der_veranstaltung",
        "msevtmgt_language",
        "_bcw_standort_value",
        "_msevtmgt_eventimage_value",
    ])

    filter_str = (
        f"msevtmgt_publishstatus eq 100000003 "
        f"and msevtmgt_eventstartdate ge {today}"
    )

    params = {
        "$select": select_fields,
        "$filter": filter_str,
        "$orderby": "msevtmgt_eventstartdate asc",
    }
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    base_url = f"{ORG_URL}/api/data/v9.2/msevtmgt_events?{query_string}"

    all_records = []
    url = base_url

    while url:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/json")
        req.add_header("OData-MaxVersion", "4.0")
        req.add_header("OData-Version", "4.0")
        req.add_header("Prefer", 'odata.include-annotations="*",odata.maxpagesize=500')

        with urllib.request.urlopen(req, context=ssl_ctx) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        records = body.get("value", [])
        all_records.extend(records)
        print(f"  Fetched {len(records)} records (total: {len(all_records)})")

        url = body.get("@odata.nextLink", None)

    return all_records


def categorize_event(name, event_type_label=""):
    """Derive event category from the event name and type label."""
    n = name.lower()
    t = event_type_label.lower()
    if "probevorlesung" in n:
        return "Probevorlesung"
    if "meet your campus" in n or "meet-your-campus" in n or "meet your campus" in t:
        return "Meet your Campus"
    if "open campus" in n or "open campus" in t:
        return "Open Campus"
    if any(k in n for k in ["infoveranstaltung", "infoabend", "inforunde",
                             "info-veranstaltung", "online-infoveranstaltung",
                             "infosession"]):
        return "Infoveranstaltung"
    if any(k in n for k in ["messe", "stuzubi", "einstieg", "vocatium",
                             "master and more", "bachelor and more",
                             "karrieretag", "abi zukunft", "parentum",
                             "jobmesse", "azubi", "horizon"]):
        return "Messe"
    if "studienberatung" in n or "studieberatung" in n:
        return "Studienberatung"
    if any(k in n for k in ["konferenz", "conference", "symposium", "forum",
                             "summit", "kongress", "tagung", "workshop",
                             "seminar", "vortrag", "lecture", "webinar",
                             "frühstück", "breakfast", "netzwerk",
                             "primary care", "alumni"]):
        return "Sonderveranstaltung"
    return "Sonstige"


def build_image_url(record):
    """Build the correct image URL from the event image lookup ID.

    The msevtmgt_eventimageurl field is unreliable (often wrong).
    Instead, we construct the URL from _msevtmgt_eventimage_value.
    """
    img_id = record.get("_msevtmgt_eventimage_value")
    if img_id:
        return f"{ASSETS_BASE}/{img_id}"
    # Fallback to msevtmgt_eventimageurl if no lookup ID
    return record.get("msevtmgt_eventimageurl") or ""


def transform_events(raw_events):
    """Map raw Dynamics records to clean JSON objects."""
    events = []
    for r in raw_events:
        # Location from OData annotation
        location = r.get(
            "_bcw_standort_value@OData.Community.Display.V1.FormattedValue", ""
        )

        # Format (Am Standort / Webinar / Hybrid)
        format_label = r.get(
            "msevtmgt_eventformat@OData.Community.Display.V1.FormattedValue", ""
        )
        if not format_label:
            fmt_val = r.get("msevtmgt_eventformat")
            mapping = {100000001: "Am Standort", 100000002: "Webinar", 100000003: "Hybrid"}
            format_label = mapping.get(fmt_val, "")

        # Event type label from Dynamics
        event_type_label = r.get(
            "msevtmgt_eventtype@OData.Community.Display.V1.FormattedValue", ""
        )

        # Art der Veranstaltung (Vor Ort / Online)
        art_label = r.get(
            "bcw_art_der_veranstaltung@OData.Community.Display.V1.FormattedValue", ""
        )

        event_name = r.get("msevtmgt_name", "")
        category = categorize_event(event_name, event_type_label)

        language_label = r.get(
            "msevtmgt_language@OData.Community.Display.V1.FormattedValue", ""
        )

        # Image name for alt text
        image_name = r.get(
            "_msevtmgt_eventimage_value@OData.Community.Display.V1.FormattedValue", ""
        )

        event = {
            "name": event_name,
            "startDate": r.get("msevtmgt_eventstartdate", ""),
            "endDate": r.get("msevtmgt_eventenddate", ""),
            "description": strip_html(r.get("msevtmgt_description", "")),
            "format": format_label,
            "formatDetail": art_label,
            "type": category,
            "typeLabel": event_type_label,
            "location": location,
            "capacity": r.get("msevtmgt_maximumeventcapacity"),
            "registrations": r.get("msevtmgt_registrationcount"),
            "imageUrl": build_image_url(r),
            "imageName": image_name,
            "registrationUrl": r.get("msevtmgt_publiceventurl", ""),
            "language": language_label,
        }
        events.append(event)
    return events


def main():
    print("Authenticating with Dynamics 365...")
    token = get_access_token()
    print("Authenticated successfully.")

    print("Fetching future published events...")
    raw = fetch_events(token)
    print(f"Total raw events: {len(raw)}")

    events = transform_events(raw)
    print(f"Transformed events: {len(events)}")

    # Stats
    with_images = sum(1 for e in events if e["imageUrl"])
    with_reg = sum(1 for e in events if e["registrationUrl"])
    categories = {}
    for e in events:
        categories[e["type"]] = categories.get(e["type"], 0) + 1

    print(f"\nStats:")
    print(f"  With images: {with_images}")
    print(f"  With registration URL: {with_reg}")
    print(f"  Categories: {json.dumps(categories, ensure_ascii=False)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"\nWritten to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
