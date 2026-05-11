"""Final validation sweep for helpqr.org production bundle."""
import glob, re, json, os, sys

ROOT = r"C:\Users\allco\Desktop\Helpqr"
html_files = glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "blog", "*.html"))

report = {
    "total": len(html_files),
    "missing_canonical": [],
    "multi_canonical": [],
    "missing_title": [],
    "missing_h1": [],
    "jsonld_errors": [],
    "jsonld_count_wrong": [],
    "blogday1_refs": [],
    "mojibake": {},
}

MOJIBAKE = ["\u00e2\u20ac\u201d", "\u00e2\u2020'", "\u00c3\u00a9", "\u00e2\u201e\u00a2", "\u00c2"]
MOJIBAKE_LABELS = ['a^EUR"', "a^+'", "A(c)", "a,cTM", "A,"]

for fp in html_files:
    with open(fp, "r", encoding="utf-8") as f:
        txt = f.read()
    name = os.path.relpath(fp, ROOT)
    # canonical
    cans = re.findall(r'<link[^>]+rel=["\']canonical["\']', txt)
    if not cans:
        cans = re.findall(r'<link[^>]+canonical', txt)
    if len(cans) == 0:
        report["missing_canonical"].append(name)
    elif len(cans) > 1:
        report["multi_canonical"].append((name, len(cans)))
    # title
    if not re.search(r'<title>[^<]+</title>', txt):
        report["missing_title"].append(name)
    # h1
    if not re.search(r'<h1[\s>]', txt, re.IGNORECASE):
        report["missing_h1"].append(name)
    # blogday1
    if "blogday1" in txt.lower():
        report["blogday1_refs"].append(name)
    # mojibake
    for pat, label in zip(MOJIBAKE, MOJIBAKE_LABELS):
        c = txt.count(pat)
        if c:
            report["mojibake"].setdefault(name, []).append((label, c))
    # JSON-LD for blog articles
    if "\\blog\\" in fp or "/blog/" in fp:
        if os.path.basename(fp) != "index.html":
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', txt, re.DOTALL)
            if len(blocks) != 3:
                report["jsonld_count_wrong"].append((name, len(blocks)))
            for i, b in enumerate(blocks):
                try:
                    json.loads(b.strip())
                except Exception as e:
                    report["jsonld_errors"].append((name, i, str(e)[:120]))

print("=== VALIDATION REPORT ===")
print(f"Total HTML files: {report['total']}")
print(f"Missing canonical: {len(report['missing_canonical'])} -> {report['missing_canonical']}")
print(f"Multiple canonicals: {len(report['multi_canonical'])} -> {report['multi_canonical']}")
print(f"Missing <title>: {len(report['missing_title'])} -> {report['missing_title']}")
print(f"Missing <h1>: {len(report['missing_h1'])} -> {report['missing_h1']}")
print(f"blogday1 refs: {len(report['blogday1_refs'])} -> {report['blogday1_refs']}")
print(f"JSON-LD parse errors: {len(report['jsonld_errors'])}")
for e in report['jsonld_errors']: print("  ", e)
print(f"JSON-LD wrong count: {len(report['jsonld_count_wrong'])}")
for e in report['jsonld_count_wrong']: print("  ", e)
print(f"Mojibake files: {len(report['mojibake'])}")
for k,v in report['mojibake'].items(): print("  ", k, v)

# Sitemap / robots / llms
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
url_count = sm.count("<url>")
has_img_ns = "xmlns:image" in sm
print(f"\nSitemap URLs: {url_count}, image namespace: {has_img_ns}")
rb = open(os.path.join(ROOT, "robots.txt"), encoding="utf-8").read()
print(f"Robots sitemap ref: {'sitemap.xml' in rb}, llms ref: {'llms.txt' in rb}")
print(f"llms.txt exists: {os.path.exists(os.path.join(ROOT, 'llms.txt'))}")

# Blog card count on blog/index.html
bi = open(os.path.join(ROOT, "blog", "index.html"), encoding="utf-8").read()
cards = len(re.findall(r'href="[^"]*blog/[^"]+"', bi))
print(f"Blog index card refs (href=blog/*): {cards}")
