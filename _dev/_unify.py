#!/usr/bin/env python3
"""Unify header + footer across blog files."""
import os, re, sys

BLOG_DIR = r"C:\Users\allco\Desktop\Helpqr\blog"

FILES = [
    "accident-alert-system","automatic-sos-alert","child-safety-tracker-india",
    "emergency-contact-widget","emergency-info-without-unlocking","emergency-safety-app",
    "family-safety-circle","inactivity-monitor-app","live-location-tracker",
    "lock-screen-emergency-contact-app","lock-screen-emergency-qr","lock-screen-emergency-qr-india",
    "lock-screen-medical-id-india","made-in-india-safety-app","medical-id-qr-code",
    "no-unlock-emergency-access-android","no-unlock-emergency-call","personal-bodyguard-app",
    "safety-app-for-night-shift","scan-to-call-emergency","senior-citizen-safety-app",
    "smart-sos-button","solo-travel-safety-app","sos-app-india","women-safety-app-2026"
]

# ── New header HTML (keep id="site-header", use Play Store href workaround)
NEW_HEADER = '''<header id="site-header" role="banner">
  <div class="header-inner">
    <a href="/" class="logo" aria-label="Help QR Home">
      <img src="/assets/logo.webp" alt="Help QR — Emergency Safety App" width="36" height="36" loading="eager" fetchpriority="high"/>
      <span class="logo-text">Help QR</span>
    </a>
    <a href="https://play.google.com/store/apps/details?id=com.qr.help.android" target="_blank" rel="noopener noreferrer" class="glass-btn">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download Free
    </a>
  </div>
</header>'''

# ── New footer HTML
NEW_FOOTER = '''<footer role="contentinfo">
  <div class="footer-inner">
    <div class="footer-logo">
      <img src="/assets/logo.webp" alt="Help QR Logo" width="34" height="34" loading="lazy"/>
      <span class="footer-logo-text">Help QR</span>
    </div>
    <p class="footer-tagline">Scan. Call. Save a Life.</p>
    <div class="footer-store-badges">
      <a href="https://play.google.com/store/apps/details?id=com.qr.help.android" target="_blank" rel="noopener noreferrer" class="footer-store-badge-link" aria-label="Get Help QR on Google Play">
        <img src="/assets/store-badge-2.svg" alt="Get it on Google Play" width="135" height="40" loading="lazy"/>
      </a>
      <a href="https://apps.apple.com/in/iphone/apps" target="_blank" rel="noopener noreferrer" class="footer-store-badge-link" aria-label="Download Help QR on App Store">
        <img src="/assets/store-badge-3.svg" alt="Download on the App Store" width="120" height="40" loading="lazy"/>
      </a>
    </div>
    <div class="footer-socials" aria-label="Follow HelpQR on social media">
      <a href="https://www.youtube.com/@HelpQR" target="_blank" rel="noopener noreferrer" class="footer-social" aria-label="HelpQR on YouTube">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.546 15.569V8.431L15.818 12l-6.272 3.569z"/></svg>
      </a>
      <a href="https://x.com/Helpqrapp" target="_blank" rel="noopener noreferrer" class="footer-social" aria-label="HelpQR on X">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      </a>
      <a href="https://www.instagram.com/helpqrapp/" target="_blank" rel="noopener noreferrer" class="footer-social" aria-label="HelpQR on Instagram">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012 4.849.07 1.366.062 2.633.334 3.608 1.308.975.975 1.246 2.242 1.308 3.608.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.062 1.366-.334 2.633-1.308 3.608-.975.975-2.242 1.246-3.608 1.308-1.265.058-1.644.07-4.849.07-3.204 0-3.584-.012-4.849-.07-1.366-.062-2.633-.334-3.608-1.308-.975-.975-1.246-2.242-1.308-3.608C2.175 15.747 2.163 15.367 2.163 12c0-3.204.012-3.584.07-4.849.062-1.366.334-2.633 1.308-3.608.975-.975 2.242-1.246 3.608-1.308C8.416 2.175 8.796 2.163 12 2.163zm0 1.838c-3.141 0-3.513.011-4.753.068-1.017.047-1.57.217-1.937.361-.487.189-.835.415-1.2.78-.364.365-.59.713-.78 1.2-.143.367-.314.92-.36 1.937-.057 1.24-.069 1.612-.069 4.753 0 3.141.011 3.513.069 4.753.046 1.017.217 1.57.36 1.937.19.487.416.835.78 1.2.365.364.713.59 1.2.78.367.143.92.314 1.937.36 1.24.057 1.612.068 4.753.068 3.141 0 3.513-.011 4.753-.068 1.017-.046 1.57-.217 1.937-.36.487-.19.835-.416 1.2-.78.364-.365.59-.713.78-1.2.143-.367.314-.92.36-1.937.057-1.24.068-1.612.068-4.753 0-3.141-.011-3.513-.068-4.753-.046-1.017-.217-1.57-.36-1.937a3.228 3.228 0 0 0-.78-1.2 3.228 3.228 0 0 0-1.2-.78c-.367-.144-.92-.314-1.937-.361-1.24-.057-1.612-.068-4.753-.068zm0 3.131a4.868 4.868 0 1 1 0 9.736 4.868 4.868 0 0 1 0-9.736zm0 8.03a3.162 3.162 0 1 0 0-6.324 3.162 3.162 0 0 0 0 6.324zm6.538-8.208a1.137 1.137 0 1 1-2.274 0 1.137 1.137 0 0 1 2.274 0z"/></svg>
      </a>
      <a href="https://www.facebook.com/helpqrapp/" target="_blank" rel="noopener noreferrer" class="footer-social" aria-label="HelpQR on Facebook">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
      </a>
    </div>
    <nav class="footer-links" aria-label="Footer navigation">
      <a href="/" class="footer-link">Home</a>
      <a href="/blog/" class="footer-link">Blog</a>
      <a href="/privacy" class="footer-link">Privacy Policy</a>
      <a href="/terms" class="footer-link">Terms &amp; Conditions</a>
      <a href="/refund" class="footer-link">Refund Policy</a>
      <a href="/delete-account" class="footer-link">Delete Account</a>
      <a href="/contact" class="footer-link">Contact</a>
    </nav>
    <p class="footer-copy">Made with <span class="heart" aria-label="love">&#9829;</span> in India &mdash; &copy; 2026 Help QR</p>
  </div>
</footer>'''

# ── New unified header+footer CSS (for blog: use literal color values)
NEW_CSS = '''/* ══════════════════════════════════════════
   HEADER — unified (pixel-identical to homepage)
══════════════════════════════════════════ */
#site-header{position:fixed;top:0;left:0;right:0;z-index:50;background:transparent;transition:background .35s,backdrop-filter .35s,box-shadow .35s;will-change:background;padding-top:env(safe-area-inset-top,0px)}
#site-header.scrolled{background:linear-gradient(135deg,rgba(255,255,255,.18) 0%,rgba(255,255,255,.08) 50%,rgba(255,255,255,.14) 100%);backdrop-filter:blur(24px) saturate(1.6) brightness(1.05);-webkit-backdrop-filter:blur(24px) saturate(1.6) brightness(1.05);box-shadow:0 4px 32px rgba(0,0,0,.12),inset 0 1px 0 rgba(255,255,255,.3),inset 0 -1px 0 rgba(255,255,255,.08);border-bottom:1px solid rgba(255,255,255,.15)}
@supports not (backdrop-filter:blur(1px)){#site-header.scrolled{background:rgba(10,3,3,.93)!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;border-bottom:1px solid rgba(140,5,8,.4)!important;box-shadow:0 2px 16px rgba(0,0,0,.45)!important}}
#site-header.scrolled .logo-text{color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.5)}
.header-inner{display:flex;align-items:center;justify-content:space-between;padding:.65rem max(1.25rem,env(safe-area-inset-right,0px)) .65rem max(1.25rem,env(safe-area-inset-left,0px));max-width:1040px;margin:0 auto}
.logo{display:flex;align-items:center;gap:.6rem;text-decoration:none}
.logo img{width:36px;height:36px;border-radius:50%;object-fit:cover;box-shadow:0 2px 10px rgba(0,0,0,.25);display:block}
.logo-text{font-family:'DM Serif Display',serif;font-size:1.05rem;color:#fff;filter:drop-shadow(0 1px 4px rgba(0,0,0,.3));text-decoration:none}
.glass-btn{display:inline-flex;align-items:center;gap:.45rem;font-family:'DM Sans',sans-serif;font-size:.8rem;font-weight:600;color:#1a0a0a;padding:.48rem 1.1rem;border-radius:99px;background:rgba(242,232,232,.93);border:1px solid rgba(255,255,255,.7);box-shadow:0 2px 14px rgba(0,0,0,.2),inset 0 1px 0 rgba(255,255,255,.9);transition:transform .2s,background .2s,box-shadow .2s;touch-action:manipulation;letter-spacing:.01em;text-decoration:none}
.glass-btn:hover{transform:scale(1.04);background:rgba(255,248,248,1);box-shadow:0 4px 20px rgba(0,0,0,.25)}
.glass-btn:active{transform:scale(.97)}
.glass-btn svg{width:13px;height:13px;flex-shrink:0;stroke:#c0080d}

/* ══════════════════════════════════════════
   FOOTER — unified (pixel-identical to homepage)
══════════════════════════════════════════ */
footer[role="contentinfo"]{padding:2.5rem 1.25rem;border-top:1px solid #f0e4e4;background:#f9f6f3}
.footer-inner{max-width:1040px;margin:0 auto;text-align:center}
.footer-logo{display:flex;align-items:center;justify-content:center;gap:.55rem;margin-bottom:.35rem}
.footer-logo img{width:34px;height:34px;border-radius:50%}
.footer-logo-text{font-family:'DM Serif Display',serif;font-size:1.05rem;color:#18191c}
.footer-tagline{color:#5a5a5a;font-size:.88rem;margin-bottom:1.25rem}
.footer-store-badges{display:flex;align-items:center;justify-content:center;gap:.6rem;flex-wrap:wrap;margin:1rem 0}
.footer-store-badge-link{display:inline-flex;flex-shrink:0;transition:transform .2s,box-shadow .2s;border-radius:.5rem;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.2)}
.footer-store-badge-link:hover{transform:scale(1.04);box-shadow:0 4px 18px rgba(0,0,0,.3)}
.footer-store-badge-link img{display:block}
.footer-socials{display:flex;align-items:center;justify-content:center;gap:1rem;margin:1rem 0 1.25rem}
.footer-social{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;color:#5a5a5a;background:transparent;transition:color .2s,background .2s,transform .2s}
.footer-social:hover{color:#ec3237;background:rgba(236,50,55,.08);transform:translateY(-2px)}
.footer-links{display:flex;flex-wrap:wrap;justify-content:center;gap:1rem 1.5rem;margin-bottom:1.25rem}
.footer-link{color:#5a5a5a;font-size:.85rem;transition:color .2s;text-decoration:none}
.footer-link:hover{color:#ec3237}
.footer-copy{color:#5a5a5a;font-size:.78rem}
.heart{color:#ec3237}'''

# ── Markers
CSS_START = "/* ══════════════════════════════════════════\n   HEADER — index12 style\n══════════════════════════════════════════ */"
# The CSS we want to replace runs from this marker to end of the FOOTER block.
# Pattern: starts with the HEADER comment, ends at the closing brace after ".site-footer-new .footer-store-badge svg"


def process(path):
    status = {"header": False, "footer": False, "css": False, "sameAs": False, "notes": []}
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()

    # ── 1) Replace header HTML
    # Pattern: <header id="site-header" role="banner"> ... </header>
    m = re.search(r'<header id="site-header" role="banner">[\s\S]*?</header>', text)
    if m:
        text = text[:m.start()] + NEW_HEADER + text[m.end():]
        status["header"] = True
    else:
        status["notes"].append("NO_HEADER_MATCH")

    # ── 2) Replace footer HTML
    m = re.search(r'<footer class="site-footer-new" role="contentinfo">[\s\S]*?</footer>', text)
    if m:
        text = text[:m.start()] + NEW_FOOTER + text[m.end():]
        status["footer"] = True
    else:
        status["notes"].append("NO_FOOTER_MATCH")

    # ── 3) Replace CSS block (HEADER comment through end of site-footer-new rules)
    # The footer CSS ends with: .site-footer-new .footer-store-badge svg{...}
    css_pattern = re.compile(
        r'/\* ══════════════════════════════════════════\s*\n'
        r'\s*HEADER\s*—\s*index12 style\s*\n'
        r'══════════════════════════════════════════ \*/'
        r'[\s\S]*?'
        r'\.site-footer-new \.footer-store-badge svg\{[^}]*\}'
    )
    m = css_pattern.search(text)
    if m:
        text = text[:m.start()] + NEW_CSS + text[m.end():]
        status["css"] = True
    else:
        status["notes"].append("NO_CSS_BLOCK_MATCH")

    # ── 4) Remove duplicate ".footer-store-badge-link" block (lines ~703-711 originally)
    dup = re.compile(
        r'\n\s*/\* Footer badge polish \*/\s*\n'
        r'\.footer-store-badge-link \{[^}]*\}\s*\n'
        r'\.footer-store-badge-link:hover \{[^}]*\}\s*\n'
        r'\.footer-store-badge-link img \{[^}]*\}'
    )
    text2, n = dup.subn('', text)
    if n:
        text = text2

    # ── 5) Remove orphan hdr-* lines in media queries
    # "  .hdr-btn { font-size:.75rem; padding:.4rem .85rem; }\n"
    text = re.sub(r'^\s*\.hdr-btn\s*\{[^}]*\}\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\.hdr-btn svg\s*\{[^}]*\}\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\.hdr-inner\s*\{[^}]*\}\s*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\.hdr-logo-text\s*\{[^}]*\}\s*\n', '', text, flags=re.MULTILINE)
    # In the `hover: none` rule, the selector list contains `.hdr-btn,` — replace with `.glass-btn,`
    text = text.replace('.faq-question, .hdr-btn, .store-badge-link', '.faq-question, .glass-btn, .store-badge-link')

    # ── 6) Update Organization JSON-LD sameAs (two formats: inline and multi-line)
    # Inline: "@type":"Organization","@id":"https://helpqr.org/#org","name":"Help QR","url":"https://helpqr.org","logo":{...}}
    # Replace the whole Organization object with one that includes sameAs
    inline_org = re.compile(
        r'(\{"@type":"Organization","@id":"https://helpqr\.org/#org","name":"Help QR","url":"https://helpqr\.org","logo":\{"@type":"ImageObject","url":"/assets/logo\.webp","width":512,"height":512\})(\})'
    )
    new_inline = (r'\1,"sameAs":["https://play.google.com/store/apps/details?id=com.qr.help.android",'
                  r'"https://apps.apple.com/in/iphone/apps",'
                  r'"https://www.youtube.com/@HelpQR",'
                  r'"https://x.com/Helpqrapp",'
                  r'"https://www.instagram.com/helpqrapp/",'
                  r'"https://www.facebook.com/helpqrapp/"]\2')
    text2, n1 = inline_org.subn(new_inline, text)
    if n1:
        text = text2
        status["sameAs"] = True

    # Multi-line format (lock-screen-emergency-qr.html etc.)
    ml_org = re.compile(
        r'("sameAs":\s*\[\s*"https://play\.google\.com/store/apps/details\?id=com\.qr\.help\.android",\s*'
        r'"https://apps\.apple\.com/in/iphone/apps"[^\]]*)\]'
    )
    # Only update if the Organization's sameAs doesn't already include youtube
    def ml_repl(m):
        block = m.group(1)
        if 'youtube.com/@HelpQR' in block:
            return m.group(0)
        # Normalize: keep the two original URLs, then append the four new ones
        return ('"sameAs": [\n'
                '        "https://play.google.com/store/apps/details?id=com.qr.help.android",\n'
                '        "https://apps.apple.com/in/iphone/apps",\n'
                '        "https://www.youtube.com/@HelpQR",\n'
                '        "https://x.com/Helpqrapp",\n'
                '        "https://www.instagram.com/helpqrapp/",\n'
                '        "https://www.facebook.com/helpqrapp/"\n'
                '      ]')
    text2, n2 = ml_org.subn(ml_repl, text)
    if n2:
        text = text2
        status["sameAs"] = True

    # ── 7) Also update Article publisher.Organization when present — add sameAs if missing
    # publisher inline: "publisher":{"@type":"Organization","name":"Help QR","url":"https://helpqr.org","logo":{"@type":"ImageObject","url":"/assets/logo.webp","width":512,"height":512}}
    pub_pattern = re.compile(
        r'("publisher":\{"@type":"Organization","name":"Help QR","url":"https://helpqr\.org","logo":\{"@type":"ImageObject","url":"/assets/logo\.webp","width":512,"height":512\})(\})'
    )
    new_pub = (r'\1,"sameAs":["https://www.youtube.com/@HelpQR",'
               r'"https://x.com/Helpqrapp",'
               r'"https://www.instagram.com/helpqrapp/",'
               r'"https://www.facebook.com/helpqrapp/"]\2')
    text2, n3 = pub_pattern.subn(new_pub, text)
    if n3:
        text = text2

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return status


def main():
    results = []
    for name in FILES:
        path = os.path.join(BLOG_DIR, name + ".html")
        if not os.path.exists(path):
            results.append((name, {"notes": ["FILE_NOT_FOUND"]}))
            continue
        r = process(path)
        results.append((name, r))
        print(f"{name}: h={r['header']} f={r['footer']} css={r['css']} sa={r['sameAs']} notes={r['notes']}")
    return results


if __name__ == "__main__":
    main()
