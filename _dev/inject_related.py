"""
Inject a Related Articles internal-linking block before <footer role="contentinfo">
in every /blog/*.html (except index.html and the noindex'd lock-screen-emergency-qr.html).
Idempotent — looks for marker <!-- HELPQR_RELATED_V1 --> and skips if already injected.

Each post receives a category-targeted set of 6 related links + a hub link, picked from
a topical cluster map so internal anchor text is contextually relevant (better than a
universal block for E-E-A-T and topical authority).
"""
import os
import re
import sys

BLOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blog")
MARKER = "<!-- HELPQR_RELATED_V1 -->"
FOOTER_RE = re.compile(r'(<footer\s+role="contentinfo">)', re.IGNORECASE)
SKIP = {"index.html", "lock-screen-emergency-qr.html"}  # hub + noindex'd duplicate

# Topical clusters — every slug belongs to exactly one cluster
CLUSTERS = {
    "lock_screen": [
        "lock-screen-emergency-qr-india", "lock-screen-medical-id-india",
        "lock-screen-emergency-contact-app", "blood-group-qr-code-lock-screen",
        "qr-code-emergency-wallpaper", "medical-id-qr-code",
        "no-unlock-emergency-call", "no-unlock-emergency-access-android",
        "emergency-info-without-unlocking", "scan-to-call-emergency",
    ],
    "women": [
        "women-safety-app-2026", "women-safety-app-free-android",
        "best-safety-app-for-women", "mahila-suraksha-app",
        "mahila-suraksha-app-hindi", "safety-app-for-girls-india",
        "personal-bodyguard-app", "safety-app-for-night-shift",
    ],
    "family": [
        "senior-citizen-safety-app", "elderly-safety-app-india",
        "family-safety-circle", "child-safety-tracker-india",
        "safety-app-people-living-alone", "inactivity-monitor-app",
        "dead-man-switch-app-india", "live-location-tracker",
    ],
    "sos": [
        "sos-app-india", "sos-alert-app-android-india",
        "smart-sos-button", "panic-button-app-india",
        "automatic-sos-alert", "emergency-safety-app",
        "emergency-app-india-free", "emergency-contact-widget",
    ],
    "crash": [
        "accident-alert-system", "crash-detection-app-india",
        "car-accident-alert-app-android", "automatic-accident-detection-india",
    ],
    "travel": [
        "solo-travel-safety-app", "made-in-india-safety-app",
    ],
}

# Human-readable anchor text — used in the related block
LABELS = {
    "lock-screen-emergency-qr-india": "Lock Screen Emergency QR India 2026",
    "lock-screen-medical-id-india": "Lock Screen Medical ID India 2026",
    "lock-screen-emergency-contact-app": "Lock Screen Emergency Contact App India",
    "blood-group-qr-code-lock-screen": "Blood Group QR Code Lock Screen India",
    "qr-code-emergency-wallpaper": "QR Code Emergency Wallpaper Android",
    "medical-id-qr-code": "Medical ID QR Code India 2026",
    "no-unlock-emergency-call": "No-Unlock Emergency Call India",
    "no-unlock-emergency-access-android": "No-Unlock Emergency Access Android",
    "emergency-info-without-unlocking": "Emergency Info Without Unlocking Phone",
    "scan-to-call-emergency": "Scan to Call Emergency India",
    "women-safety-app-2026": "Women Safety App India 2026",
    "women-safety-app-free-android": "Best Free Women Safety App Android 2026",
    "best-safety-app-for-women": "Best Safety App for Women India 2026",
    "mahila-suraksha-app": "Mahila Suraksha App India 2026",
    "mahila-suraksha-app-hindi": "महिला सुरक्षा ऐप 2026 — हिंदी गाइड",
    "safety-app-for-girls-india": "Best Safety App for Girls India 2026",
    "personal-bodyguard-app": "Personal Bodyguard App India 2026",
    "safety-app-for-night-shift": "Safety App for Night Shift Workers 2026",
    "senior-citizen-safety-app": "Senior Citizen Safety App India",
    "elderly-safety-app-india": "Best Elderly Safety App India 2026",
    "family-safety-circle": "Family Safety Circle App India",
    "child-safety-tracker-india": "Child Safety Tracker India 2026",
    "safety-app-people-living-alone": "Best Safety App for People Living Alone India",
    "inactivity-monitor-app": "Inactivity Monitor App India 2026",
    "dead-man-switch-app-india": "Dead Man Switch Safety App India 2026",
    "live-location-tracker": "Live Location Tracker India 2026",
    "sos-app-india": "Best SOS App India 2026",
    "sos-alert-app-android-india": "Best SOS Alert App Android India 2026",
    "smart-sos-button": "Smart SOS Button India 2026",
    "panic-button-app-india": "Best Panic Button App India 2026",
    "automatic-sos-alert": "Automatic SOS Alert India 2026",
    "emergency-safety-app": "Best Emergency Safety App India 2026",
    "emergency-app-india-free": "Best Free Emergency App India 2026",
    "emergency-contact-widget": "Emergency Contact Widget Android India",
    "accident-alert-system": "Accident Alert System India 2026",
    "crash-detection-app-india": "Best Crash Detection App India 2026",
    "car-accident-alert-app-android": "Best Car Accident Alert App Android 2026",
    "automatic-accident-detection-india": "Automatic Accident Detection App India 2026",
    "solo-travel-safety-app": "Solo Travel Safety App India 2026",
    "made-in-india-safety-app": "Made in India Safety App 2026",
}

SLUG_TO_CLUSTER = {slug: name for name, slugs in CLUSTERS.items() for slug in slugs}

# Cross-cluster "spillover" picks — 2 strong articles from sibling clusters
# so every related-block also surfaces 2 lateral pillars (not just same-topic)
SPILLOVER = {
    "lock_screen": ["sos-app-india", "emergency-safety-app"],
    "women":       ["lock-screen-emergency-qr-india", "sos-app-india"],
    "family":      ["lock-screen-emergency-qr-india", "emergency-safety-app"],
    "sos":         ["lock-screen-emergency-qr-india", "women-safety-app-2026"],
    "crash":       ["sos-app-india", "lock-screen-emergency-qr-india"],
    "travel":      ["sos-app-india", "lock-screen-emergency-qr-india"],
}


def pick_related(current_slug: str):
    """Return up to 6 slugs related to current_slug, never including itself."""
    cluster = SLUG_TO_CLUSTER.get(current_slug)
    related = []
    if cluster:
        for s in CLUSTERS[cluster]:
            if s != current_slug and s in LABELS:
                related.append(s)
            if len(related) >= 4:
                break
        for s in SPILLOVER.get(cluster, []):
            if s != current_slug and s not in related and s in LABELS:
                related.append(s)
            if len(related) >= 6:
                break
    # Top-up from a fallback list if cluster was small
    fallback = ["sos-app-india", "women-safety-app-2026", "lock-screen-emergency-qr-india",
                "lock-screen-medical-id-india", "accident-alert-system", "emergency-app-india-free"]
    for s in fallback:
        if len(related) >= 6:
            break
        if s != current_slug and s not in related:
            related.append(s)
    return related[:6]


CARD_TPL = (
    '<li><a href="/blog/{slug}" '
    'style="display:block;padding:.85rem 1rem;background:#fff;border:1px solid #f0e4e4;'
    'border-radius:.75rem;color:#18191c;text-decoration:none;font-weight:500;font-size:.92rem;'
    'box-shadow:0 2px 8px rgba(0,0,0,.04);transition:transform .2s,box-shadow .2s;">'
    '{label} &rarr;</a></li>'
)

def build_block(slug: str) -> str:
    related = pick_related(slug)
    cards = "\n      ".join(CARD_TPL.format(slug=s, label=LABELS[s]) for s in related)
    return f"""
{MARKER}
<section aria-labelledby="related-heading-{slug}" style="max-width:1040px;margin:0 auto;padding:2.5rem 1.25rem 1rem;border-top:1px solid #f0e4e4;background:#f9f6f3;">
  <h2 id="related-heading-{slug}" style="font-family:'DM Serif Display',serif;font-size:1.35rem;color:#18191c;margin-bottom:1.25rem;text-align:center;">More India Safety Guides</h2>
  <ul style="list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:.85rem;">
      {cards}
  </ul>
  <p style="text-align:center;margin-top:1.5rem;"><a href="/blog/" style="display:inline-block;padding:.65rem 1.4rem;background:#8C0508;color:#fff;border-radius:99px;font-size:.88rem;font-weight:600;text-decoration:none;">View all 40 guides &rarr;</a></p>
</section>
"""


def main():
    files = sorted(f for f in os.listdir(BLOG_DIR)
                   if f.endswith(".html") and f not in SKIP)
    injected, skipped, errors = 0, 0, []
    for fname in files:
        path = os.path.join(BLOG_DIR, fname)
        slug = fname[:-5]
        try:
            with open(path, "r", encoding="utf-8") as fh:
                html = fh.read()
            if MARKER in html:
                skipped += 1
                continue
            m = FOOTER_RE.search(html)
            if not m:
                errors.append(f"{fname}: <footer role=\"contentinfo\"> not found")
                continue
            block = build_block(slug)
            new_html = html[:m.start()] + block + "\n" + html[m.start():]
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_html)
            injected += 1
        except Exception as e:
            errors.append(f"{fname}: {e}")
    print(f"Injected:   {injected}")
    print(f"Skipped (already had marker): {skipped}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
