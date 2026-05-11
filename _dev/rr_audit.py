"""Emulates Google Rich Results Test checks locally against all 31 blog HTML files."""
import json, re, glob, os
from urllib.parse import urlparse

os.chdir(r"C:\Users\allco\Desktop\Helpqr\blog")

REQ_ARTICLE = ["headline", "image", "datePublished", "author", "publisher"]
REQ_HOWTO   = ["name", "step"]
REQ_ORG     = ["name", "url"]
REQ_APP     = ["name", "operatingSystem", "offers"]
REQ_AGG     = ["ratingValue", "reviewCount"]

def check_url(u):
    if not isinstance(u, str): return "not-string"
    p = urlparse(u)
    if p.scheme not in ("http", "https"): return "not-absolute"
    return None

errors = []
warnings = []

for f in sorted(glob.glob("*.html")):
    if f == "index.html": continue
    html = open(f, encoding="utf-8").read()
    blocks = re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', html)

    data = []
    for i, b in enumerate(blocks):
        try: data.append(json.loads(b))
        except Exception as e:
            errors.append((f, "JSON_PARSE", f"block {i}", str(e)[:120]))

    ents = []
    for d in data:
        if isinstance(d, dict) and "@graph" in d:
            ents.extend(d["@graph"])
        else:
            ents.append(d)

    # Article
    arts = [e for e in ents if isinstance(e, dict) and e.get("@type") in ("Article", "BlogPosting", "NewsArticle")]
    if not arts: errors.append((f, "MISSING", "Article", ""))
    for a in arts:
        for r in REQ_ARTICLE:
            if r not in a: errors.append((f, "Article_missing", r, ""))
        img = a.get("image")
        if isinstance(img, dict):
            u = img.get("url"); err = check_url(u) if u else "no-url"
            if err: errors.append((f, "Article.image", err, u or ""))
            if "width" not in img or "height" not in img:
                warnings.append((f, "Article.image", "missing-width-height", ""))
        elif isinstance(img, str):
            err = check_url(img)
            if err: errors.append((f, "Article.image", err, img))
        elif isinstance(img, list):
            for x in img:
                u = x.get("url") if isinstance(x, dict) else x
                err = check_url(u)
                if err: errors.append((f, "Article.image", err, str(u)[:80]))
        else:
            errors.append((f, "Article.image", "invalid-type", type(img).__name__))
        au = a.get("author")
        if isinstance(au, dict):
            if not au.get("name"): errors.append((f, "Article.author", "missing-name", ""))
            if au.get("url") and check_url(au["url"]):
                errors.append((f, "Article.author.url", "bad", au["url"]))
        pub = a.get("publisher")
        if isinstance(pub, dict):
            if not pub.get("name"): errors.append((f, "Article.publisher", "missing-name", ""))
            logo = pub.get("logo")
            if isinstance(logo, dict):
                lu = logo.get("url"); err = check_url(lu) if lu else "no-url"
                if err: errors.append((f, "Article.publisher.logo", err, lu or ""))
        if "dateModified" not in a:
            warnings.append((f, "Article", "missing-dateModified", ""))

    # BreadcrumbList
    bcs = [e for e in ents if isinstance(e, dict) and e.get("@type") == "BreadcrumbList"]
    if not bcs: errors.append((f, "MISSING", "BreadcrumbList", ""))
    for bc in bcs:
        it = bc.get("itemListElement", [])
        if not isinstance(it, list) or len(it) < 2:
            errors.append((f, "Breadcrumb", "too-short", len(it) if isinstance(it, list) else 0))
        for j, li in enumerate(it):
            if li.get("@type") != "ListItem": errors.append((f, "Breadcrumb", "bad-type", j))
            if "position" not in li: errors.append((f, "Breadcrumb", "missing-position", j))
            if "name" not in li: errors.append((f, "Breadcrumb", "missing-name", j))
            if "item" not in li and j < len(it) - 1:
                errors.append((f, "Breadcrumb", "missing-item", j))
            if "item" in li:
                u = li["item"]
                if isinstance(u, dict): u = u.get("@id") or u.get("url")
                err = check_url(u) if u else "no-url"
                if err: errors.append((f, "Breadcrumb.item", err, u or ""))

    # FAQPage
    faqs = [e for e in ents if isinstance(e, dict) and e.get("@type") == "FAQPage"]
    for fq in faqs:
        me = fq.get("mainEntity", [])
        if not isinstance(me, list) or not me:
            errors.append((f, "FAQ", "empty-mainEntity", ""))
        seen = set()
        for j, q in enumerate(me):
            if q.get("@type") != "Question":
                errors.append((f, "FAQ", "bad-Q-type", j))
            n = q.get("name", "").strip()
            if not n: errors.append((f, "FAQ", "Q-no-name", j))
            if n in seen: errors.append((f, "FAQ", "Q-duplicate", n[:60]))
            seen.add(n)
            aa = q.get("acceptedAnswer")
            if not isinstance(aa, dict) or aa.get("@type") != "Answer":
                errors.append((f, "FAQ", "bad-A-type", j))
            at = (aa.get("text", "") if isinstance(aa, dict) else "").strip()
            if not at: errors.append((f, "FAQ", "A-no-text", j))

    # HowTo
    hts = [e for e in ents if isinstance(e, dict) and e.get("@type") == "HowTo"]
    for ht in hts:
        for r in REQ_HOWTO:
            if r not in ht: errors.append((f, "HowTo_missing", r, ""))
        steps = ht.get("step", [])
        if not isinstance(steps, list) or len(steps) < 2:
            errors.append((f, "HowTo", "too-few-steps", len(steps) if isinstance(steps, list) else 0))
        for j, s in enumerate(steps):
            if s.get("@type") != "HowToStep": errors.append((f, "HowTo.step", "bad-type", j))
            if not s.get("name") and not s.get("text"):
                errors.append((f, "HowTo.step", "missing-name-and-text", j))

    # Organization
    orgs = [e for e in ents if isinstance(e, dict) and e.get("@type") == "Organization"]
    for org in orgs:
        for r in REQ_ORG:
            if r not in org: errors.append((f, "Org_missing", r, ""))
        if "url" in org and check_url(org["url"]): errors.append((f, "Org.url", "bad", org["url"]))
        logo = org.get("logo")
        if isinstance(logo, dict):
            lu = logo.get("url"); err = check_url(lu) if lu else "no-url"
            if err: errors.append((f, "Org.logo", err, lu or ""))
        elif isinstance(logo, str):
            err = check_url(logo)
            if err: errors.append((f, "Org.logo", err, logo))

    # MobileApplication / SoftwareApplication
    apps = [e for e in ents if isinstance(e, dict) and e.get("@type") in ("MobileApplication", "SoftwareApplication")]
    for ap in apps:
        for r in REQ_APP:
            if r not in ap: errors.append((f, "App_missing", r, ""))
        offers = ap.get("offers")
        if isinstance(offers, dict):
            if "price" not in offers: errors.append((f, "App.offers", "missing-price", ""))
            if "priceCurrency" not in offers: errors.append((f, "App.offers", "missing-priceCurrency", ""))
        ag = ap.get("aggregateRating")
        if isinstance(ag, dict):
            for r in REQ_AGG:
                if r not in ag: errors.append((f, "App.aggregateRating_missing", r, ""))
            rc = ag.get("reviewCount")
            try:
                if int(rc) < 1: errors.append((f, "App.aggregateRating.reviewCount", "<1", rc))
            except: errors.append((f, "App.aggregateRating.reviewCount", "non-int", rc))

    # Canonical parity
    canon_m = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', html) or \
              re.search(r'<link[^>]*href="([^"]+)"[^>]*rel="canonical"', html)
    canon = canon_m.group(1) if canon_m else None
    if not canon: errors.append((f, "CANONICAL", "missing", ""))
    elif arts:
        mop = arts[0].get("mainEntityOfPage")
        mop_id = mop.get("@id") if isinstance(mop, dict) else mop
        if mop_id and mop_id != canon:
            warnings.append((f, "canonical-vs-mainEntityOfPage", "mismatch", f"{canon} != {mop_id}"))

print("=== ERRORS ===")
for e in errors: print(e)
print(f"\nTotal errors: {len(errors)}")
print(f"Total warnings: {len(warnings)}")
print("\n=== WARNING SAMPLE (first 30) ===")
for w in warnings[:30]: print(w)
print(f"\n=== WARNING TYPES ===")
from collections import Counter
print(Counter((w[1], w[2]) for w in warnings).most_common())
