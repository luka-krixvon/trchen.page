#!/usr/bin/env python3
"""Refresh the citation count and Zenodo statistics in content.json.

    python3 refresh_metrics.py && python3 build.py

The figures are baked into the built pages, so they are refreshed here rather
than fetched in the visitor's browser. Run it by hand, or let the daily
GitHub Actions workflow do it.

A source that is rate limiting or down is retried a few times and then skipped:
the figure already on file is kept rather than being zeroed, and the script
still exits 0 so an unattended run does not report failure over a blip.
"""
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request
from datetime import date

HERE = pathlib.Path(__file__).parent
CJ = HERE / "content.json"
S2 = ("https://api.semanticscholar.org/graph/v1/paper/batch"
      "?fields=title,citationCount,externalIds")
UA = {"User-Agent": "personal-site-metrics/1.0 (+https://github.com/luka-krixvon)"}
ATTEMPTS = 4


def fetch(url, data=None, label=""):
    """GET or POST JSON, retrying on rate limits and transient errors."""
    headers = dict(UA)
    if data is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            return json.load(urllib.request.urlopen(req, timeout=45))
        except urllib.error.HTTPError as ex:
            retryable = ex.code in (429, 500, 502, 503, 504)
            print("  %s: HTTP %s%s" % (label or url, ex.code,
                                       "" if retryable else " (giving up)"))
            if not retryable:
                return None
        except Exception as ex:
            print("  %s: %s" % (label or url, ex))
        if attempt < ATTEMPTS:
            wait = 5 * 2 ** (attempt - 1)      # 5s, 10s, 20s
            print("     retrying in %ds (%d/%d)" % (wait, attempt + 1, ATTEMPTS))
            time.sleep(wait)
    return None


def ident(pub):
    for url in pub.get("links", {}).values():
        if "arxiv.org/abs/" in url:
            return "arXiv:" + url.rsplit("/", 1)[-1]
        if "doi.org/" in url:
            return "DOI:" + url.split("doi.org/", 1)[1]
    return None


def main():
    c = json.loads(CJ.read_text(encoding="utf-8"))
    changed = []

    m = c.get("metrics") or {}
    aid = m.get("openalex_id")
    if not aid or "citations" not in c["counts"]:
        print("  citation figures not shown on the page; skipping OpenAlex")
    else:
        a = fetch("https://api.openalex.org/authors/%s" % aid, label="openalex %s" % aid)
        stats = (a or {}).get("summary_stats") or {}
        got = {
            "citations": (a or {}).get("cited_by_count"),
            "h_index":   stats.get("h_index"),
            "i10_index": stats.get("i10_index"),
        }
        if a and all(v is not None for v in got.values()):
            for k, v in got.items():
                if c["counts"].get(k) != v:
                    changed.append("%s %s -> %s" % (k, c["counts"].get(k), v))
                c["counts"][k] = v
            print("  openalex: %(citations)s citations, h-index %(h_index)s, i10 %(i10_index)s" % got)
        else:
            print("  openalex unavailable; figures left at %s" % c["counts"].get("citations"))

    for dep in c.get("deposits", []):
        rid = dep.get("record")
        if not rid:
            continue
        r = fetch("https://zenodo.org/api/records/%s" % rid, label="zenodo %s" % rid)
        if not r:
            continue
        st = r.get("stats") or {}
        # Zenodo's own record page shows the unique counts, so match it
        v, d = st.get("unique_views"), st.get("unique_downloads")
        if (dep.get("views"), dep.get("downloads")) != (v, d):
            changed.append("%s %s/%s -> %s/%s" % (rid, dep.get("views"), dep.get("downloads"), v, d))
        dep["views"], dep["downloads"] = v, d
        print("  %5s views %4s downloads  %s" % (v, d, dep["title"][:46]))

    if not changed:
        # stamping the date on an unchanged file would make an empty commit every day
        print("\nno figures moved; content.json left alone")
        return 0
    c["site"]["metrics_updated"] = date.today().isoformat()
    CJ.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nchanged: " + "; ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
