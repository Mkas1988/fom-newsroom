#!/usr/bin/env python3
"""
Static Site Generator for FOM Newsroom article pages.
Fetches all articles from the MyNewsdesk API and generates one static HTML page
per article at /{slug}/index.html with full content, SEO meta tags, and related articles.
"""

import html
import json
import math
import os
import re
import ssl
import time
import urllib.request
from datetime import datetime

API_KEY = "2J8377Ow95pCNFI_DPzZTQ"
BASE_URL = "https://www.mynewsdesk.com/services/pressroom"
SITE_URL = "https://newsroom.fomhochschule.com"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIKEL_HTML = os.path.join(SCRIPT_DIR, "artikel.html")

TYPE_LABELS = {
    "pressrelease": "News",
    "news": "News",
    "event": "Event",
    "blog_post": "Blog",
    "image": "Bild",
    "video": "Video",
    "document": "Dokument",
}

GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

try:
    import certifi
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_ctx = ssl.create_default_context()


# ─── Helpers (ported from generate-sitemap.py / artikel.html JS) ───

def to_slug(title):
    """Convert title to URL slug (max 115 chars)."""
    slug = title.lower()
    for k, v in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}.items():
        slug = slug.replace(k, v)
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    if len(slug) > 115:
        slug = slug[:115].rsplit("-", 1)[0]
    return slug


def strip_html(text):
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def escape(text):
    """HTML-escape text."""
    return html.escape(text, quote=True) if text else ""


def format_date(date_val):
    """Format a date value to German date string like '01. Januar 2026'."""
    if not date_val:
        return ""
    dt_str = date_val.get("datetime", "") if isinstance(date_val, dict) else str(date_val)
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return f"{dt.day:02d}. {GERMAN_MONTHS[dt.month]} {dt.year}"
    except (ValueError, KeyError):
        return ""


def normalize_date(d):
    """Normalize date to dict with 'datetime' key."""
    if not d:
        return None
    if isinstance(d, dict) and "datetime" in d:
        return d
    if isinstance(d, str):
        return {"datetime": d}
    return None


def normalize_tags(tags):
    """Normalize tags from API response (can be array, object, or nested)."""
    if not tags:
        return []
    if isinstance(tags, list):
        return [t.get("name", t) if isinstance(t, dict) else str(t) for t in tags]
    if isinstance(tags, dict) and "tag" in tags:
        t = tags["tag"]
        if isinstance(t, list):
            return [x.get("name", x) if isinstance(x, dict) else str(x) for x in t]
        return [t.get("name", t) if isinstance(t, dict) else str(t)]
    return []


def normalize_contacts(cp):
    """Normalize contact_people from API response."""
    if not cp:
        return []
    if isinstance(cp, list):
        return cp
    if isinstance(cp, dict) and "contact_person" in cp:
        c = cp["contact_person"]
        return c if isinstance(c, list) else [c]
    return []


def normalize_related_items(ri):
    """Normalize related_items from API response."""
    if not ri:
        return []
    if isinstance(ri, list):
        return ri
    if isinstance(ri, dict) and "related_item" in ri:
        r = ri["related_item"]
        return r if isinstance(r, list) else [r]
    return []


def get_article_authors(contacts, related_items):
    """Filter contacts to only those linked via related_items."""
    author_ids = {
        str(r.get("item_id", ""))
        for r in related_items
        if r.get("type_of_media") == "contact_person"
    }
    if not author_ids:
        return []
    return [c for c in contacts if str(c.get("id", "")) in author_ids]


# ─── API ───

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


def fetch_article_detail(item_id, media_type):
    """Fetch full article detail via /view/ endpoint."""
    url = (
        f"{BASE_URL}/view/{API_KEY}"
        f"?format=json&type_of_media={media_type}&item_id={item_id}"
    )
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, context=ssl_ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("item", None)


# ─── Template extraction ───

def extract_template():
    """Read artikel.html and split into head/foot templates."""
    with open(ARTIKEL_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Split at articleContainer div
    marker = '<div id="articleContainer">'
    idx = content.index(marker)

    head = content[:idx]
    rest = content[idx:]

    # Find end of articleContainer content (the closing </div> before footer)
    # articleContainer contains the loading spinner, then closes
    footer_marker = "<!-- Footer -->"
    footer_idx = rest.index(footer_marker)
    foot = rest[footer_idx:]

    # Replace title placeholder
    head = re.sub(
        r"<title>[^<]*</title>",
        "<title>{{TITLE}}</title>",
        head,
    )
    # Replace meta description
    head = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="{{DESCRIPTION}}">',
        head,
    )
    # Replace canonical
    head = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        '<link rel="canonical" href="{{CANONICAL}}">',
        head,
    )

    # Convert relative asset paths to absolute (for subdirectory pages)
    # Font URLs in @font-face
    head = re.sub(r"url\('fonts/", "url('/fonts/", head)
    # Preload hrefs
    head = re.sub(r'href="fonts/', 'href="/fonts/', head)
    # Image srcs
    head = re.sub(r'src="fom-logo', 'src="/fom-logo', head)
    head = re.sub(r'src="FOM_NewsRoom', 'src="/FOM_NewsRoom', head)
    head = re.sub(r'src="akkreditierung', 'src="/akkreditierung', head)

    # Fix footer asset paths too
    foot = re.sub(r'src="fom-logo', 'src="/fom-logo', foot)
    foot = re.sub(r'src="FOM_NewsRoom', 'src="/FOM_NewsRoom', foot)
    foot = re.sub(r'src="akkreditierung', 'src="/akkreditierung', foot)
    foot = re.sub(r'href="medien.html"', 'href="/medien.html"', foot)
    foot = re.sub(r'href="kontakt.html"', 'href="/kontakt.html"', foot)
    foot = re.sub(r'src="auth.js"', 'src="/auth.js"', foot)

    # Fix header nav links to absolute
    head = re.sub(r'href="medien.html"', 'href="/medien.html"', head)
    head = re.sub(r'href="kontakt.html"', 'href="/kontakt.html"', head)
    head = re.sub(r'src="auth.js"', 'src="/auth.js"', head)

    # Add OG tags and JSON-LD placeholder after canonical
    og_tags = """
    <meta property="og:type" content="article">
    <meta property="og:title" content="{{OG_TITLE}}">
    <meta property="og:description" content="{{DESCRIPTION}}">
    <meta property="og:url" content="{{CANONICAL}}">
    <meta property="og:image" content="{{OG_IMAGE}}">
    <meta property="og:site_name" content="FOM Newsroom">
    <meta name="twitter:card" content="summary_large_image">
    {{JSON_LD}}"""
    head = head.replace(
        '<link rel="canonical" href="{{CANONICAL}}">',
        '<link rel="canonical" href="{{CANONICAL}}">' + og_tags,
    )

    return head, foot


# ─── Rendering ───

def render_share_buttons(share_url, share_title):
    """Render the share button HTML."""
    su = html.escape(share_url, quote=True)
    st = html.escape(share_title, quote=True)
    return f'''<div class="hero-share">
                                <span class="share-label">TEILEN</span>
                                <a href="mailto:?subject={st}&amp;body={su}" class="share-btn" title="E-Mail"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22,6 12,13 2,6"/></svg></a>
                                <a href="https://www.linkedin.com/sharing/share-offsite/?url={su}" target="_blank" rel="noopener" class="share-btn" title="LinkedIn"><svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a>
                                <a href="https://www.facebook.com/sharer/sharer.php?u={su}" target="_blank" rel="noopener" class="share-btn" title="Facebook"><svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></a>
                                <a href="https://bsky.app/intent/compose?text={st}%20{su}" target="_blank" rel="noopener" class="share-btn" title="Bluesky"><svg viewBox="0 0 24 24"><path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.594 6.456.756 2.822 3.465 3.753 5.985 3.496-4.01.553-7.122 2.385-2.852 8.098C8.242 27.228 10.66 20.772 12 17.835c1.34 2.937 3.271 9.044 8.273 3.983 4.27-5.713 1.158-7.545-2.852-8.098 2.52.257 5.228-.674 5.985-3.496C23.622 9.418 24 4.458 24 3.768c0-.69-.139-1.86-.902-2.203-.659-.3-1.664-.62-4.3 1.24C16.046 4.747 13.087 8.686 12 10.8z"/></svg></a>
                                <a href="https://twitter.com/intent/tweet?url={su}&amp;text={st}" target="_blank" rel="noopener" class="share-btn" title="X"><svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>
                                <button class="share-btn" title="Link kopieren" onclick="navigator.clipboard.writeText(window.location.href); this.innerHTML='<svg viewBox=&quot;0 0 24 24&quot;><polyline points=&quot;20 6 9 17 4 12&quot; fill=&quot;none&quot; stroke=&quot;currentColor&quot; stroke-width=&quot;2&quot;/></svg>'; setTimeout(() => this.innerHTML='<svg viewBox=&quot;0 0 24 24&quot;><path d=&quot;M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71&quot; fill=&quot;none&quot; stroke=&quot;currentColor&quot; stroke-width=&quot;2&quot;/><path d=&quot;M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71&quot; fill=&quot;none&quot; stroke=&quot;currentColor&quot; stroke-width=&quot;2&quot;/></svg>', 1500);"><svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" fill="none" stroke="currentColor" stroke-width="2"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" fill="none" stroke="currentColor" stroke-width="2"/></svg></button>
                                <span class="share-spacer"></span>
                                <span class="reading-time">{{READING_TIME}} Min. Lesezeit</span>
                            </div>'''


def render_article_content(item, slug, all_articles, tag_index):
    """Render the article HTML content (replaces articleContainer innerHTML)."""
    tags = normalize_tags(item.get("tags"))
    contacts = normalize_contacts(item.get("contact_people"))
    related_items_raw = normalize_related_items(item.get("related_items"))
    authors = get_article_authors(contacts, related_items_raw)
    image_url = item.get("image") or item.get("image_medium") or ""
    published_at = normalize_date(item.get("published_at"))

    # Reading time
    plain_text = strip_html(item.get("body", ""))
    word_count = len(plain_text.split()) if plain_text else 0
    reading_minutes = max(1, round(word_count / 200))

    canonical_url = f"{SITE_URL}/{slug}/"
    share_url = urllib.request.quote(canonical_url, safe="")
    share_title = urllib.request.quote(item.get("header", ""), safe="")

    article_html = ""

    # Hero
    tags_html = ""
    if tags:
        tag_links = "".join(
            f'<a href="/?search={urllib.request.quote(t, safe="")}" class="hero-tag">{escape(t)}</a>'
            for t in tags
        )
        tags_html = f'<div class="hero-tags">{tag_links}</div>'

    share_html = render_share_buttons(share_url, share_title)
    share_html = share_html.replace("{{READING_TIME}}", str(reading_minutes))

    article_html += f'''
                    <section class="article-hero">
                        <div class="article-hero-inner">
                            <div class="article-meta">
                                <span class="article-date">{escape(format_date(published_at))}</span>
                            </div>
                            {tags_html}
                            <h1>{escape(item.get("header", ""))}</h1>
                            {f'<p class="article-summary">{escape(item.get("summary", ""))}</p>' if item.get("summary") else ""}
                            {share_html}
                        </div>
                    </section>'''

    # Image
    if image_url:
        caption = item.get("image_caption", "")
        article_html += f'''
                        <div class="article-image-wrap">
                            <img class="article-image" src="{escape(image_url)}" alt="{escape(caption)}">
                            {f'<p class="article-image-caption">{escape(caption)}</p>' if caption else ""}
                        </div>'''

    # Body
    body = item.get("body", "")
    if body:
        # Normalize sub-headings: h3-h6 -> h2
        normalized_body = re.sub(r"<(/?)h[3-6](\s|>)", r"<\1h2\2", body, flags=re.IGNORECASE)
        article_html += f'''
                        <div class="article-content">
                            <div class="article-body">{normalized_body}</div>
                        </div>'''

    # Author
    if authors:
        c = authors[0]
        avatar_url = c.get("image_thumbnail_large") or c.get("image_thumbnail_medium") or c.get("image_small") or ""
        author_role = c.get("specialist") or c.get("title") or ""
        author_name = c.get("name", "")
        if avatar_url:
            avatar_html = f'<img class="author-avatar" src="{escape(avatar_url)}" alt="{escape(author_name)}">'
        else:
            initial = author_name[0] if author_name else "?"
            avatar_html = f'<div class="author-avatar-placeholder">{escape(initial)}</div>'

        article_html += f'''
                        <div class="article-author">
                            <span class="author-label">Autor</span>
                            <a href="/autor.html?id={escape(str(c.get("id", "")))}" class="author-link">
                                {avatar_html}
                                <span class="author-info">
                                    <span class="author-name">{escape(author_name)}</span>
                                    {f'<span class="author-role">{escape(author_role)}</span>' if author_role else ""}
                                </span>
                            </a>
                        </div>'''

    # Back link
    article_html += '''
                    <div class="back-link">
                        <a href="/">&larr; Zur&uuml;ck zum Newsroom</a>
                    </div>'''

    # Related articles
    related_html = render_related_articles(item, slug, all_articles, tag_index)
    if related_html:
        article_html += related_html

    return article_html


def render_related_articles(current_item, current_slug, all_articles, tag_index):
    """Compute and render 'Das konnte Sie auch interessieren' section."""
    current_id = str(current_item.get("id", ""))
    current_type = current_item.get("_media_type", "pressrelease")
    tags = normalize_tags(current_item.get("tags"))

    related = []
    seen_ids = {current_id}

    # Step 1: Tag-based matching (first tag)
    if tags:
        first_tag = tags[0]
        candidates = tag_index.get(first_tag, [])
        for a in candidates:
            aid = str(a.get("id", ""))
            if aid not in seen_ids:
                related.append(a)
                seen_ids.add(aid)
            if len(related) >= 3:
                break

    # Step 2: Supplement with recent same-type articles
    if len(related) < 3:
        for a in all_articles:
            if a.get("_media_type") == current_type:
                aid = str(a.get("id", ""))
                if aid not in seen_ids:
                    related.append(a)
                    seen_ids.add(aid)
                if len(related) >= 3:
                    break

    # Step 3: If still not enough, use any recent article
    if len(related) < 3:
        for a in all_articles:
            aid = str(a.get("id", ""))
            if aid not in seen_ids:
                related.append(a)
                seen_ids.add(aid)
            if len(related) >= 3:
                break

    related = related[:3]
    if not related:
        return ""

    cards = ""
    for ri in related:
        ri_date = normalize_date(ri.get("published_at"))
        ri_image = ri.get("image_medium") or ri.get("image_small") or ri.get("image") or ""
        ri_type = ri.get("_media_type") or ri.get("type_of_media") or "pressrelease"
        ri_slug = to_slug(ri.get("header", ""))

        img_html = f'<img class="related-card-image" src="{escape(ri_image)}" alt="" loading="lazy">' if ri_image else ""
        cards += f'''
                                    <a href="/{ri_slug}/" class="related-card">
                                        {img_html}
                                        <div class="related-card-body">
                                            <div class="related-card-type">{escape(TYPE_LABELS.get(ri_type, ri_type))}</div>
                                            <div class="related-card-title">{escape(ri.get("header", ""))}</div>
                                            <div class="related-card-date">{escape(format_date(ri_date))}</div>
                                        </div>
                                    </a>'''

    return f'''
                        <section class="related-section">
                            <h2 class="related-title">Das k&ouml;nnte Sie auch interessieren</h2>
                            <div class="related-grid">
                                {cards}
                            </div>
                        </section>'''


def render_json_ld(item, slug):
    """Render JSON-LD structured data for a NewsArticle."""
    published_at = normalize_date(item.get("published_at"))
    updated_at = normalize_date(item.get("updated_at"))
    image_url = item.get("image") or item.get("image_medium") or ""

    ld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": item.get("header", ""),
        "url": f"{SITE_URL}/{slug}/",
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE_URL}/{slug}/"},
        "publisher": {
            "@type": "Organization",
            "name": "FOM Hochschule",
            "url": "https://www.fom.de",
        },
    }

    if image_url:
        ld["image"] = image_url
    if item.get("summary"):
        ld["description"] = item["summary"][:200]
    if published_at and published_at.get("datetime"):
        ld["datePublished"] = published_at["datetime"]
    if updated_at and updated_at.get("datetime"):
        ld["dateModified"] = updated_at["datetime"]

    # Author
    contacts = normalize_contacts(item.get("contact_people"))
    related_items_raw = normalize_related_items(item.get("related_items"))
    authors = get_article_authors(contacts, related_items_raw)
    if authors:
        ld["author"] = {
            "@type": "Person",
            "name": authors[0].get("name", ""),
        }

    return f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'


def render_page(item, slug, head_template, foot_template, all_articles, tag_index):
    """Render a complete HTML page for one article."""
    title = f"{item.get('header', 'Artikel')} \u2013 FOM Newsroom"
    summary = item.get("summary") or strip_html(item.get("body", "")) or item.get("header", "")
    description = summary[:160]
    canonical = f"{SITE_URL}/{slug}/"
    image_url = item.get("image") or item.get("image_medium") or ""

    # Fill head template
    head = head_template
    head = head.replace("{{TITLE}}", escape(title))
    head = head.replace("{{DESCRIPTION}}", escape(description))
    head = head.replace("{{CANONICAL}}", escape(canonical))
    head = head.replace("{{OG_TITLE}}", escape(item.get("header", "")))
    head = head.replace("{{OG_IMAGE}}", escape(image_url))
    head = head.replace("{{JSON_LD}}", render_json_ld(item, slug))

    # Render article content
    content = render_article_content(item, slug, all_articles, tag_index)

    # Wrap in articleContainer
    article_container = f'    <div id="articleContainer">{content}\n    </div>\n\n    '

    return head + article_container + foot_template


# ─── Redirect rules ───

def generate_redirect_rules(all_articles):
    """Generate .htaccess redirect rules for old URL patterns (id+type -> slug)."""
    rules = []
    for item in all_articles:
        item_id = str(item.get("id", ""))
        slug = to_slug(item.get("header", ""))
        if item_id and slug:
            rules.append(
                f"RewriteCond %{{QUERY_STRING}} ^id={re.escape(item_id)}"
                f" [OR]\n"
                f"RewriteCond %{{QUERY_STRING}} id={re.escape(item_id)}&\n"
                f"RewriteRule ^artikel\\.html$ /{slug}/? [R=301,L]\n"
            )
    return "\n".join(rules)


# ─── Main ───

def main():
    print("=" * 60)
    print("FOM Newsroom - Static Article Generator")
    print("=" * 60)

    # 1. Extract template
    print("\n1. Extracting template from artikel.html...")
    head_template, foot_template = extract_template()
    print("   Template extracted successfully.")

    # 2. Fetch all articles (list endpoint)
    print("\n2. Fetching article lists...")
    print("   Fetching pressreleases...")
    pressreleases = fetch_articles("pressrelease")
    print("   Fetching news...")
    news = fetch_articles("news")

    all_articles = []
    for item in pressreleases:
        item["_media_type"] = "pressrelease"
        all_articles.append(item)
    for item in news:
        item["_media_type"] = "news"
        all_articles.append(item)

    print(f"   Total articles: {len(all_articles)}")

    # 3. Fetch full details for each article
    print("\n3. Fetching article details...")
    detailed_articles = []
    seen_slugs = set()

    for i, item in enumerate(all_articles):
        header = item.get("header", "")
        item_id = item.get("id", "")
        if not header or not item_id:
            continue

        slug = to_slug(header)
        if slug in seen_slugs:
            print(f"   [{i+1}/{len(all_articles)}] SKIP (duplicate slug): {slug}")
            continue
        seen_slugs.add(slug)

        print(f"   [{i+1}/{len(all_articles)}] Fetching: {slug}")
        try:
            detail = fetch_article_detail(item_id, item["_media_type"])
            if detail:
                detail["_media_type"] = item["_media_type"]
                # Preserve list data for related articles matching
                detail["_list_image_medium"] = item.get("image_medium", "")
                detail["_list_image_small"] = item.get("image_small", "")
                detailed_articles.append(detail)
            else:
                print(f"   WARNING: No detail found for {item_id}")
        except Exception as e:
            print(f"   ERROR fetching {item_id}: {e}")

        # Small delay to avoid rate limiting
        time.sleep(0.1)

    print(f"   Fetched details for {len(detailed_articles)} articles.")

    # 4. Build tag index (for related articles)
    print("\n4. Building tag index...")
    tag_index = {}
    for a in detailed_articles:
        for tag in normalize_tags(a.get("tags")):
            tag_index.setdefault(tag, []).append(a)
    print(f"   {len(tag_index)} unique tags indexed.")

    # 5. Generate static pages
    print("\n5. Generating static HTML pages...")
    generated = 0
    id_to_slug = {}

    for item in detailed_articles:
        slug = to_slug(item.get("header", ""))
        if not slug:
            continue

        # Track ID->slug mapping for redirects
        item_id = str(item.get("id", ""))
        if item_id:
            id_to_slug[item_id] = slug

        # Render page
        page_html = render_page(item, slug, head_template, foot_template, all_articles, tag_index)

        # Write to {slug}/index.html
        output_dir = os.path.join(SCRIPT_DIR, slug)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "index.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(page_html)

        generated += 1

    print(f"   Generated {generated} article pages.")

    # 6. Generate redirect rules
    print("\n6. Generating redirect rules...")
    redirect_rules = generate_redirect_rules(detailed_articles)
    redirect_file = os.path.join(SCRIPT_DIR, "_article_redirects.htaccess")
    with open(redirect_file, "w", encoding="utf-8") as f:
        f.write("# Auto-generated article ID->slug redirects\n")
        f.write("# Include this in .htaccess or paste the rules\n\n")
        f.write(redirect_rules)
    print(f"   Redirect rules written to _article_redirects.htaccess")

    # Summary
    print("\n" + "=" * 60)
    print(f"Done! Generated {generated} static article pages.")
    print(f"Output: {SCRIPT_DIR}/{{slug}}/index.html")
    print("=" * 60)


if __name__ == "__main__":
    main()
