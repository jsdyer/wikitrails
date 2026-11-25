"""Render honest, static search metadata from the same inputs as the page."""
from html import escape, unescape
import json
import re


def add_search_metadata(page, tool, *, category="UtilitiesApplication", datasets=()):
    slug = tool["id"]
    on_coolcode = (slug != "coolcode-tool-template"
                  and tool["source"].rstrip("/") == f"https://github.com/jsdyer/{slug}")
    canonical = "https://coolcode.ca" + tool["url"] if on_coolcode else None
    title = re.search(r"<title>(.*?)</title>", page, re.S)
    if not title or page.count("</head>") != 1:
        raise ValueError("Search metadata needs one page title and head")
    app = {
        "@type": "WebApplication", "name": tool["title"],
        "description": tool["description"], "applicationCategory": category,
        "operatingSystem": "Any operating system with a modern web browser",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CAD"},
    }
    if canonical:
        app.update({"@id": canonical + "#application", "url": canonical})
    if datasets:
        app["about"] = [{"@id": dataset["@id"]} for dataset in datasets]
    graph = {"@context": "https://schema.org", "@graph": [app, *datasets]}
    # A source title or description must never terminate the script element.
    encoded = json.dumps(graph, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    tags = [f'<script type="application/ld+json">{encoded}</script>',
            f'<meta property="og:title" content="{escape(unescape(title.group(1)), quote=True)}">',
            f'<meta property="og:description" content="{escape(tool["description"], quote=True)}">',
            '<meta property="og:type" content="website">']
    if canonical:
        tags.append(f'<meta property="og:url" content="{escape(canonical, quote=True)}">')
        if not re.search(r'<link\b[^>]*\brel=[\"\x27]canonical[\"\x27]', page, re.I):
            tags.append(f'<link rel="canonical" href="{escape(canonical, quote=True)}">')
    return page.replace("</head>", "\n" + "\n".join(tags) + "\n</head>")
