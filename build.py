#!/usr/bin/env python3
"""Generate the site from content.json.

    python3 build.py

Writes index.html (English), zh/index.html, ja/index.html, sitemap.xml, robots.txt,
plus preview/ — a self-contained copy for pasting into a preview tool, where the
YouTube players are stand-ins instead of real embeds.
"""
import html
import json
import pathlib

HERE = pathlib.Path(__file__).parent
C = json.loads((HERE / "content.json").read_text(encoding="utf-8"))
SITE, COUNTS, PUBS, PATS, LANGS = C["site"], C["counts"], C["publications"], C["patents"], C["languages"]
DEMO_VIDEO = False
AWARDS, APPS, DEPS = C["awards"], C["appearances"], C["deposits"]
METRICS = C.get("metrics") or {}

e = lambda s: html.escape(str(s), quote=True)


def ver(rel):
    """Short content hash, so a changed asset gets a new URL."""
    import hashlib
    return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()[:8]
mmss = lambda s: "%d:%02d" % (s // 60, s % 60)

PREVIEW_TITLE = "學者網站 A+C 版"

PLAY = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M0 0l10 5-10 5z"/></svg>'
CAP = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 1 9l11 6 9-4.91V17h2V9zM5 '
       '13.18v4L12 21l7-3.82v-4L12 17z"/></svg>')


def authors(pub):
    return ", ".join("<b>%s</b>" % e(SITE["name"]) if a == "@me" else e(a) for a in pub["authors"])


def topbar(L, code, depth):
    up = "../" * depth
    nav = "".join('<a href="#%s">%s</a>' % (k, e(L["nav"][k]))
                  for k in (["about", "research", "publications"]
                            + (["deposits"] if DEPS else []) + (["patents"] if PATS else []) + ["awards"]))
    langs = "".join(
        '<a href="%s" hreflang="%s"%s>%s</a>' % (
            e(up + (l["dir"] + "/" if l["dir"] else "")), e(l["hreflang"]),
            ' aria-current="page"' if l["code"] == code else "", e(l["label"]))
        for l in LANGS)
    return f"""<header class="topbar">
  <nav class="topnav" aria-label="{e(L['nav']['about'])}">{nav}</nav>
  <div class="topbar-r">
    <nav class="langs" aria-label="Language">{langs}</nav>
    <button class="themebtn" type="button" data-theme-toggle aria-label="{e(L['ui']['theme_toggle'])}">◐</button>
  </div>
</header>"""


def identity(L, code, depth):
    up = "../" * depth
    avatar = (f'<img class="portrait" src="{e(up + SITE["photo"])}" alt="{e(SITE["name"])}" width="128" height="128">'
              if SITE.get("photo") else
              f'<div class="portrait" aria-hidden="true">{e(SITE["monogram"])}</div>')
    labels = {"scholar": "Google Scholar", "orcid": "ORCID", "linkedin": "LinkedIn",
              "github": "GitHub", "youtube": "YouTube"}
    order = [SITE.get("primary_link")] + [k for k in labels if k != SITE.get("primary_link")]
    links = [(labels[k], SITE[k]) for k in order if k in labels and SITE.get(k)]
    linkrow = "".join('<a href="%s" rel="me">%s</a>' % (e(u), e(n)) for n, u in links)
    return f"""<header class="idblock">
  {avatar}
  <div class="idtext">
    <h1>{(e(L['name_local']) + ' ') if L.get('name_local') else ''}{e(SITE['name'])}</h1>
    <p class="fields">{e(L['role'])}</p>
    <p class="meta">{e(L['location'])} · <a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></p>
    <nav class="idlinks" aria-label="Profiles">{linkrow}</nav>
  </div>
</header>"""


def publication(pub, L, i, code):
    v, cid = pub.get("video"), pub["id"]
    if v and v.get("id") in ("", "VIDEO_ID") and not DEMO_VIDEO:
        v = None          # a placeholder id never ships a dead player
    acts = "".join('<a href="%s">%s</a>' % (e(u), e(k.upper() if k in ("pdf", "bibtex") else k.capitalize()))
                   for k, u in pub["links"].items())
    def pick(field):
        x = pub.get(field)
        if isinstance(x, dict):
            return x.get(code) or x.get("en")
        return x
    sm, cb = pick("summary"), pick("contribution")
    blurb = ""
    if sm or cb:
        blurb = '<div class="pub-blurb">%s%s</div>' % (
            ('<p>%s</p>' % e(sm)) if sm else "",
            ('<p class="pub-contrib"><b>%s</b>%s</p>'
             % (e(L["ui"]["contribution"]), e(cb))) if cb else "")
    watch = panel = mark = ""
    if v:
        pid = "talk-" + cid
        watch = ""
        mark = '<span class="pub-talk">%s%s</span>' % (PLAY, e(v["duration"]))
        chaps = "".join(
            '<button class="chap" type="button" data-seek="%d"><time>%s</time><span>%s</span></button>'
            % (sec, mmss(sec), e(txt)) for sec, txt in L["chapters"].get(cid, []))
        panel = f"""
            <div class="vpanel" id="{pid}">
              <div class="yt" data-yt="{e(v['id'])}" data-title="{e(pub['title'])}">
                <button class="yt-face" type="button" aria-label="{e(pub['title'])}">
                  <span class="yt-play">{PLAY}</span>
                </button>
                <span class="yt-dur">{e(v['duration'])}</span>
                <span class="yt-demo">{e(L['ui']['demo_note'])}</span>
              </div>
              <div class="chapters">
                <div class="chaphead"><b>{e(L['ui']['chapters'])}</b><span class="talklang">{e(L['ui']['talk_lang'])}</span></div>
                {chaps}
              </div>
            </div>"""
    note = (" · " + e(L["notes"][pub["note"]])) if pub.get("note") else ""
    venue = L["venues"].get(pub.get("venue_key", ""), pub.get("venue", ""))
    tags = "".join('<span class="tag">%s</span>' % e(L["filters"][t]) for t in pub["topics"])
    pid2 = "pub-" + cid
    return f"""        <li class="pub" data-topics="{e(' '.join(pub['topics']))}" data-video="{1 if v else 0}">
          <button class="pub-head" type="button" data-pubtoggle aria-expanded="false" aria-controls="{pid2}">
            <span class="pub-y">{pub['year']}</span>
            <span class="pub-ttl">{e(pub['title'])}</span>
            <span class="pub-src">{mark}{e(pub.get('source',''))}</span>
          </button>
          <div class="pub-body{' has-talk' if v else ''}" id="{pid2}" hidden>
            {panel}
            {blurb}
            <div class="pub-meta">
            <p class="pub-a">{authors(pub)}</p>
            <p class="pub-v">{e(venue)}{note}</p>
            <div class="tags">{tags}</div>
            <div class="acts">{acts}{watch}</div>
            </div>
          </div>
        </li>"""


def body(L, code, depth):
    up = "../" * depth
    lab = L["count_labels"]
    headline = "".join(
        '<div><b>%s</b><span>%s</span></div>' % (COUNTS[k], e(lab[k]))
        for k in ("citations", "h_index", "publications", "patents")
        if COUNTS.get(k) is not None)
    minor = "".join(
        '<span>%s<b>%s</b></span>' % (e(lab[k]), COUNTS[k])
        for k in ("i10_index", "deposits", "awards")
        if COUNTS.get(k) is not None)
    src = ""
    if METRICS.get("source") and METRICS.get("updated"):
        srclink = '<a href="%s">%s</a>' % (e(METRICS["source_url"]), e(METRICS["source"]))
        src = '<p class="kpi-src">%s</p>' % (
            e(L["ui"]["metrics_note"]).replace("%s", "{}", 2).format(srclink, e(METRICS["updated"])))
    counts = ('<div class="kpi-main">%s</div><div class="kpi-strip">%s</div>%s'
              % (headline, minor, src))
    lede_html = ('          <p class="lede">%s</p>\n' % L["lede"]) if L.get("lede") else ""
    bio_html = "".join('<p class="bio">%s</p>' % e(par) for par in L["bio"].split("\n\n"))
    cv_class = "cv-grid cv-stack" if len(L["education"]) < 2 else "cv-grid"
    edu = "".join('<div class="cv-row"><dt>%s</dt><dd>%s</dd></div>' % (e(y), e(x)) for y, x in L["education"])
    pos = "".join('<div class="cv-row"><dt>%s</dt><dd>%s</dd></div>' % (e(y), e(x)) for y, x in L["positions"])
    themes = "".join('<div class="theme-row"><h3>%s</h3><p>%s</p></div>' % (e(a), e(b))
                     for a, b in L["themes"])
    pub_sub = "<p>%s</p>" % e(L["ui"]["pub_sub"])
    used = [k for k in ("routing", "privacy", "systems", "evaluation", "bioinformatics", "applications")
            if any(k in p["topics"] for p in PUBS)]
    keys = ["all"] + used + (["video"] if any(p.get("video") for p in PUBS) else [])
    filters = "".join(
        '<button class="filt" type="button" data-filter="%s" aria-pressed="%s">%s</button>'
        % (k, "true" if k == "all" else "false", e(L["filters"][k])) for k in keys)
    pubs = "\n".join(publication(p, L, i + 1, code) for i, p in enumerate(PUBS))
    rows = ""
    for p in PATS:
        st = L["patent_status"][p["status"]]
        cls = {"granted": "b-ok", "allowed": "b-mid", "examining": "b-wait"}[p["status"]]
        ttl = p["title"].get(code) or p["title"]["en"]
        extra = ""
        rows += ('<tr><td class="t-no"><span class="jur">%s</span></td>'
                 '<td class="t-no">%s</td><td class="t-ttl">%s%s</td>'
                 '<td><span class="badge %s"><i></i>%s</span></td></tr>'
                 % (e(p["region"]), e(p["no"]), e(ttl), extra, cls, e(st)))
    dc = L["deposit_cols"]
    dep_rows = "".join(
        '<a class="dep" href="https://doi.org/%s"><span class="jur">%s</span>'
        '<span class="dep-t">%s</span>%s<span class="t-doi">doi:%s</span></a>'
        % (e(x["doi"]), e(L["deposit_kinds"][x["kind"]]), e(x["title"]),
           ('<span class="dep-stat">%s</span>' % e(
               L["ui"]["dep_stats"].replace("{v}", str(x["views"])).replace("{d}", str(x["downloads"]))))
           if x.get("views") is not None else "",
           e(x["doi"]))
        for x in DEPS)
    ac = L["award_cols"]
    years, aw_rows = [], ""
    for a in AWARDS:
        if a["year"] not in years:
            years.append(a["year"])
    for y in sorted(years):
        items = "".join(
            '<li><span class="aw-win">%s</span><b>%s</b>'
            '<span class="aw-comp">%s</span>%s</li>'
            % (e(a["award"].get(code) or a["award"]["en"]),
               e(a["project"].get(code) or a["project"]["en"]),
               e(a["short"].get(code) or a["short"]["en"]),
               ('<span class="aw-org">%s</span>'
                % e(a["issuer"].get(code) or a["issuer"]["en"])) if a.get("issuer") else "")
            for a in AWARDS if a["year"] == y)
        aw_rows += ('<div class="road-y"><span class="road-node"></span>'
                    '<span class="road-year">%s</span><ul>%s</ul></div>' % (y, items))
    def app_row(x):
        label = e(x["what"].get(code) or x["what"]["en"])
        head = '<a href="%s">%s ↗</a>' % (e(x["url"]), label) if x.get("url") else label
        t = x.get("title")
        if isinstance(t, dict):
            t = t.get(code) or t.get("en")
        sub = '<span class="app-title">%s</span>' % e(t) if t else ""
        return '<div class="svc"><dt>%s</dt><dd>%s%s</dd></div>' % (x["year"], head, sub)
    apps = "".join(app_row(x) for x in APPS)
    pc = L["patent_cols"]
    patents_section = "" if not PATS else f"""<section class="sec" id="patents">
      <div class="sec-head"><h2 class="big">{e(L['headings']['patents'])}</h2></div>
      <div class="tablewrap"><table>
        <thead><tr><th>{e(pc['region'])}</th><th>{e(pc['no'])}</th><th>{e(pc['title'])}</th><th>{e(pc['status'])}</th></tr></thead>
        <tbody>{rows}</tbody>
      </table></div>
      <p class="filt-note">{e(L['ui']['patent_note'])}</p>
    </section>"""
    return f"""<a class="skip" href="#about">{e(L['ui']['skip'])}</a>
{topbar(L, code, depth)}
<main class="page" id="main">
{identity(L, code, depth)}
  <div class="col">
    <div class="kpi">{counts}</div>

    <section class="sec" id="about">
      <span class="eyebrow">{e(L['headings']['about'])}</span>
      {bio_html}
      <div class="{cv_class}">
        <dl class="cv-group"><h3>{e(L['headings']['education'])}</h3>{edu}</dl>
        <dl class="cv-group"><h3>{e(L['headings']['positions'])}</h3>{pos}</dl>
      </div>
    </section>

    <section class="sec" id="research">
      <span class="eyebrow">{e(L['headings']['research'])}</span>
      <div class="inner-themes">{themes}</div>
    </section>

    <section class="sec" id="publications">
      <div class="sec-head"><h2 class="big">{e(L['headings']['publications'])}</h2>{pub_sub}</div>
      <div class="filters">{filters}</div>
      <p class="filt-note" data-filter-note data-tpl="{e(L['ui']['filter_note'].replace('{total}', str(len(PUBS))))}"></p>
      <ol>
{pubs}
      </ol>
    </section>

    <section class="sec" id="deposits">
      <div class="sec-head"><h2 class="big">{e(L['headings']['deposits'])}</h2></div>
      <div class="dep-grid">{dep_rows}</div>
    </section>

    {patents_section}

    <section class="sec" id="awards">
      <div class="sec-head"><h2 class="big">{e(L['headings']['awards'])}</h2></div>
      <div class="road" style="--road-cols:{len(set(a['year'] for a in AWARDS))}">{aw_rows}</div>
    </section>

    <section class="sec" id="appearances">
      <div class="sec-head"><h2 class="big">{e(L['headings']['appearances'])}</h2></div>
      <div class="app-list">{apps}</div>
    </section>

    <footer class="site">
      <span>{e(SITE['name'])} · {e(SITE['email'])}</span>
      <span>{e(L['ui']['updated'])}</span>
    </footer>
  </div>
</main>"""


def jsonld(L, code):
    base = SITE["domain"].rstrip("/")
    url = base + "/" + (dict((l["code"], l["dir"]) for l in LANGS)[code] + "/" if code != "en" else "")
    g = [{
        "@type": "Person", "@id": base + "/#person", "name": SITE["name"],
        "url": url, "email": "mailto:" + SITE["email"], "jobTitle": L["role"],
        "description": L["bio"],
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": n} for n in SITE["alumni_of"]],
        "worksFor": [{"@type": "Organization", "name": n}
                     for n in ([SITE["works_for"]] if isinstance(SITE["works_for"], str) else SITE["works_for"])],
        "alternateName": SITE["name_zh"],
        "image": base + "/" + SITE["photo"],
        "knowsAbout": [v for k, v in L["filters"].items() if k not in ("all", "video")],
        "sameAs": [u for u in (SITE["scholar"], SITE["orcid"], SITE["github"],
                               SITE["youtube"], SITE.get("linkedin", "")) if u],
    }]
    for p in PUBS:
        links = p.get("links") or {}
        art = {
            "@type": "ScholarlyArticle", "@id": base + "/#" + p["id"], "headline": p["title"],
            "name": p["title"], "datePublished": str(p["year"]), "inLanguage": "en",
            "author": [({"@type": "Person", "@id": base + "/#person", "name": SITE["name"]}
                        if a == "@me" else {"@type": "Person", "name": a}) for a in p["authors"]],
            "publication": {"@type": "PublicationEvent", "name": L["venues"].get(p.get("venue_key", ""), "")},
        }
        canonical = links.get("DOI") or links.get("arXiv")
        if canonical:
            art["url"] = canonical
        same = sorted({u for u in links.values() if u})
        if same:
            art["sameAs"] = same
        ids = []
        for key, prefix in (("arXiv", "arXiv:"), ("DOI", "doi:")):
            u = links.get(key)
            if u:
                tail = u.rstrip("/").split("doi.org/", 1)[-1] if key == "DOI" else u.rstrip("/").rsplit("/", 1)[-1]
                ids.append(prefix + tail)
        if ids:
            art["identifier"] = ids if len(ids) > 1 else ids[0]
        g.append(art)
        v = p.get("video")
        if v:
            g.append({
                "@type": "VideoObject", "name": p["title"],
                "description": L["chapters"].get(p["id"], [[0, p["title"]]])[0][1],
                "uploadDate": v["uploaded"], "duration": v["iso"], "inLanguage": "en",
                "thumbnailUrl": "https://i.ytimg.com/vi/%s/maxresdefault.jpg" % v["id"],
                "embedUrl": "https://www.youtube.com/embed/%s" % v["id"],
                "contentUrl": "https://www.youtube.com/watch?v=%s" % v["id"],
                "about": {"@id": base + "/#" + p["id"]},
                "hasPart": [{"@type": "Clip", "name": txt, "startOffset": sec,
                             "url": "https://www.youtube.com/watch?v=%s&t=%ds" % (v["id"], sec)}
                            for sec, txt in L["chapters"].get(p["id"], [])],
            })
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, indent=1)


def page(code, demo=False, standalone=True):
    L, depth = C[code], 0 if (code == "en" or demo) else 1
    up = "../" * depth
    css, js = (HERE / "assets" / "style.css").read_text(encoding="utf-8"), (HERE / "assets" / "site.js").read_text(encoding="utf-8")
    base = SITE["domain"].rstrip("/")
    alts = "".join('<link rel="alternate" hreflang="%s" href="%s/%s">' % (
        e(l["hreflang"]), base, l["dir"] + "/" if l["dir"] else "") for l in LANGS)
    alts += '<link rel="alternate" hreflang="x-default" href="%s/">' % base
    dirs = dict((l["code"], l["dir"]) for l in LANGS)
    canon = base + "/" + (dirs[code] + "/" if code != "en" else "")
    oglocales = {"en": "en_US", "zh": "zh_TW", "ja": "ja_JP"}
    oglocale = oglocales.get(code, "en_US")
    oglocale_alt = "".join('<meta property="og:locale:alternate" content="%s">' % v
                           for k, v in oglocales.items() if k != code and k in C)
    cjk = {"zh": "&family=Noto+Sans+TC:wght@400;500;700;900",
           "ja": "&family=Noto+Sans+JP:wght@400;500;700;900"}.get(code, "")
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700'
             + cjk + '&display=swap">')
    if demo:
        globals()["DEMO_VIDEO"] = True
        b = body(L, code, 0)
        globals()["DEMO_VIDEO"] = False
        for l in LANGS:  # preview pages sit side by side, not in language folders
            b = b.replace('href="%s"' % (l["dir"] + "/" if l["dir"] else ""),
                          'href="%s"' % ("index.html" if l["code"] == "zh" else l["code"] + ".html"))
        head = (f'<meta name="claude:viewport-fit-sides" content="cover">\n<title>{e(PREVIEW_TITLE)}</title>\n'
                f'{fonts}\n<style>{css}</style>')
        inner = f'{head}\n<div data-demo-root>{b}</div>\n<script>document.documentElement.dataset.demo="1";\n{js}</script>'
        if not standalone:
            return inner
        return (f'<!doctype html>\n<html lang="{e(L["lang_attr"])}" data-demo="1">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                f'<title>{e(L["meta_title"])}</title>\n{fonts}\n<style>{css}</style>\n</head>\n<body>\n{b}\n'
                f'<script>{js}</script>\n</body>\n</html>\n')
    return f"""<!doctype html>
<html lang="{e(L['lang_attr'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(L['meta_title'])}</title>
<meta name="description" content="{e(L['meta_desc'])}">
<link rel="canonical" href="{canon}">
{alts}
<meta name="author" content="{e(SITE['name'])}">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{oglocale}">
{oglocale_alt}
<meta property="og:title" content="{e(L['meta_title'])}">
<meta property="og:description" content="{e(L['meta_desc'])}">
<meta property="og:image" content="{base}/{e(SITE['og_image'])}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(L['meta_title'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(L['meta_title'])}">
<meta name="twitter:description" content="{e(L['meta_desc'])}">
<meta name="twitter:image" content="{base}/{e(SITE['og_image'])}">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{up}favicon-96.png" sizes="96x96" type="image/png">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<meta name="theme-color" content="#FAFAF9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16191A" media="(prefers-color-scheme: dark)">
{fonts}
<link rel="stylesheet" href="{up}assets/style.css?v={ver("assets/style.css")}">
</head>
<body>
{body(L, code, depth)}
<script type="application/ld+json">
{jsonld(L, code)}
</script>
<script src="{up}assets/site.js?v={ver("assets/site.js")}" defer></script>
</body>
</html>
"""


def main():
    written = []
    for l in LANGS:
        out = HERE / (l["dir"] + "/index.html" if l["dir"] else "index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(l["code"]), encoding="utf-8")
        written.append(out.relative_to(HERE))

    base = SITE["domain"].rstrip("/")
    urls = "".join("<url><loc>%s/%s</loc>%s</url>" % (
        base, l["dir"] + "/" if l["dir"] else "",
        "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s/%s"/>' % (
            a["hreflang"], base, a["dir"] + "/" if a["dir"] else "") for a in LANGS))
        for l in LANGS)
    (HERE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">%s</urlset>\n' % urls, encoding="utf-8")
    (HERE / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % base, encoding="utf-8")
    written += [pathlib.Path("sitemap.xml"), pathlib.Path("robots.txt")]

    prev = HERE / "preview"
    prev.mkdir(exist_ok=True)
    (prev / "index.html").write_text(page("zh", demo=True, standalone=False), encoding="utf-8")
    for code in ("en", "ja"):
        (prev / (code + ".html")).write_text(page(code, demo=True), encoding="utf-8")
    written += [pathlib.Path("preview/index.html"), pathlib.Path("preview/en.html"), pathlib.Path("preview/ja.html")]

    for w in written:
        print("  ", w)
    print("built", len(written), "files")


if __name__ == "__main__":
    main()
