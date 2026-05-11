"""
Rebuild blog/index.html with a more-clickable layout:
  - Featured 3-pillar hero section
  - Category filter chips (live JS filtering)
  - NEW + PILLAR badges on cards
  - Reading-time chip + 1-line excerpt per card
  - Stronger hover and arrow-slide micro-interaction
Idempotent: it FULLY REGENERATES the file every run from the data table below.
Preserves: <head>, header, footer (templates copied verbatim from the old file).
"""
import os, json

CDN = "https://helpqr-static.b-cdn.net/blogs_webp"

# ── DATA TABLE ────────────────────────────────────────────────────────────────
# Order matters: pillars first, then chronological newest → older.
POSTS = [
    # (slug, title, cat_code, cat_label, image_basename, excerpt, mins, flag)
    # PILLARS — top of grid + featured
    ("sos-app-india", "Best SOS App India 2026",
     "sos", "Core SOS", "sos-app-india",
     "India's free SOS app that works offline — GPS delivered in 6–8 seconds.", 7, "PILLAR"),
    ("lock-screen-emergency-qr-india", "Lock Screen Emergency QR India 2026",
     "lock-screen", "Lock Screen", "lock-screen-emergency-qr-india",
     "QR wallpaper any bystander scans without unlocking — medical ID + contacts.", 7, "PILLAR"),
    ("women-safety-app-2026", "Women Safety App India 2026",
     "women", "Women Safety", "women-safety-app-india",
     "Privacy-first protection without a panic button — silent SOS from lock screen.", 7, "PILLAR"),

    # DAY-3 NEW (2026-04-29)
    ("automatic-accident-detection-india", "Automatic Accident Detection App India 2026",
     "crash-travel", "Crash & Travel", "automatic-accident-detection-india",
     "Gyroscope crash SOS — GPS sent automatically, works without internet.", 5, "NEW"),
    ("mahila-suraksha-app-hindi", "महिला सुरक्षा ऐप 2026 — हिंदी गाइड",
     "women", "Women Safety", "mahila-suraksha-app-hindi",
     "पूरा हिंदी इंटरफेस — bina internet, lock screen से SOS, बिल्कुल मुफ्त।", 5, "NEW"),
    ("safety-app-for-girls-india", "Best Safety App for Girls India 2026",
     "women", "Women Safety", "safety-app-for-girls-india",
     "Silent SOS for students — live location for parents, offline-first design.", 5, "NEW"),
    ("safety-app-people-living-alone", "Best Safety App for People Living Alone India 2026",
     "family", "Family & Senior", "safety-app-people-living-alone",
     "Daily check-in plus auto-SOS if you don't respond — for solo living.", 5, "NEW"),

    # DAY-2 (2026-04-26)
    ("emergency-app-india-free", "Best Free Emergency App India 2026",
     "sos", "Core SOS", "emergency-app-india-free",
     "Truly free SOS — no subscription, no ads, no login. Works offline via SMS.", 6, None),
    ("women-safety-app-free-android", "Best Free Women Safety App Android India 2026",
     "women", "Women Safety", "women-safety-app-free-android",
     "Silent SOS that fires from a locked screen — for women on Indian commutes.", 6, None),
    ("dead-man-switch-app-india", "Dead Man Switch Safety App India 2026",
     "family", "Family & Senior", "dead-man-switch-app-india",
     "Auto-alert if you miss check-in — for solo trekkers and night-shift workers.", 5, None),
    ("car-accident-alert-app-android", "Best Car Accident Alert App Android India 2026",
     "crash-travel", "Crash & Travel", "car-accident-alert-app-android",
     "Gyroscope crash detection sends GPS in 6–8 seconds, even without internet.", 6, None),
    ("mahila-suraksha-app", "Mahila Suraksha App India 2026",
     "women", "Women Safety", "mahila-suraksha-app",
     "Lock screen SOS in Hindi/Hinglish — bina internet ke kaam karta hai.", 5, None),
    ("panic-button-app-india", "Best Panic Button App India 2026",
     "sos", "Core SOS", "panic-button-app-india",
     "One-tap SOS from a locked screen with offline SMS fallback to your Help Circle.", 5, None),

    # DAY-1 (2026-04-24)
    ("sos-alert-app-android-india", "Best SOS Alert App Android India 2026",
     "sos", "Core SOS", "sos-alert-app-android-india",
     "Best Android SOS apps tested on Indian networks — locked-screen ready.", 5, None),
    ("best-safety-app-for-women", "Best Safety App for Women India 2026",
     "women", "Women Safety", "best-safety-app-for-women",
     "Silent SOS, live location, zero unlock — the 2026 women's safety review.", 5, None),
    ("qr-code-emergency-wallpaper", "QR Code Emergency Wallpaper Android India",
     "lock-screen", "Lock Screen", "qr-code-emergency-wallpaper",
     "Generate and set a QR wallpaper in 2 minutes — bystanders scan to call you.", 5, None),
    ("blood-group-qr-code-lock-screen", "Blood Group QR Code Lock Screen India",
     "lock-screen", "Lock Screen", "blood-group-qr-code-lock-screen",
     "Blood group visible without unlocking — life-saver in India's road accidents.", 5, None),
    ("elderly-safety-app-india", "Best Elderly Safety App India 2026",
     "family", "Family & Senior", "elderly-safety-app-india",
     "Fall alert, inactivity check, family peace — tailored for Indian elderly.", 5, None),
    ("crash-detection-app-india", "Best Crash Detection App India 2026",
     "crash-travel", "Crash & Travel", "crash-detection-app-india",
     "Accelerometer-driven crash alert for 2-wheeler riders on Indian highways.", 5, None),

    # CORE / HIGH-VALUE
    ("accident-alert-system", "Accident Alert System India 2026",
     "crash-travel", "Crash & Travel", "accident-alert-system-india",
     "Why your phone fails in a crash and how Inactivity Monitor saves the day.", 6, None),
    ("automatic-sos-alert", "Automatic SOS Alert India 2026",
     "sos", "Core SOS", "automatic-sos-alert-india",
     "The 24-hour Inactivity Monitor — passive dead-man's switch for solo travel.", 6, None),
    ("child-safety-tracker-india", "Child Safety Tracker India 2026",
     "family", "Family & Senior", "child-safety-tracker-india",
     "Live location plus SOS for school-age children, parent-managed Help Circle.", 5, None),
    ("emergency-contact-widget", "Emergency Contact Widget India 2026",
     "sos", "Core SOS", "emergency-contact-widget-india",
     "Home-screen widget with one-tap SOS — no app open, no PIN needed.", 4, None),
    ("emergency-safety-app", "Best Emergency Safety App India 2026",
     "sos", "Core SOS", "emergency-safety-app",
     "Full-stack emergency tooling — Lock Screen QR, SOS, Inactivity, all free.", 6, None),
    ("family-safety-circle", "Family Safety Circle India 2026",
     "family", "Family & Senior", "senior-citizen-safety-app-india",
     "Help Circle — the 2–5 trusted people your emergency alerts reach first.", 5, None),
    ("inactivity-monitor-app", "Inactivity Monitor App India 2026",
     "family", "Family & Senior", "inactivity-monitor-app-india",
     "The core 24-hour mechanism that fires alerts when you cannot.", 5, None),
    ("live-location-tracker", "Live Location Tracker India 2026",
     "family", "Family & Senior", "live-location-tracker-india",
     "Real-time location sharing with the Help Circle — only during an emergency.", 4, None),
    ("made-in-india-safety-app", "Made in India Safety App 2026",
     "crash-travel", "Crash & Travel", "made-in-india-safety-app",
     "Offline-first, 2G-ready, Bharat-built — works in zero-network rural India.", 5, None),
    ("medical-id-qr-code", "Medical ID QR Code India 2026",
     "lock-screen", "Lock Screen", "medical-id-qr-code-india",
     "Scannable health card on your wallpaper — 108 ambulance compatible.", 6, None),
    ("no-unlock-emergency-call", "No-Unlock Emergency Call India 2026",
     "lock-screen", "Lock Screen", "no-unlock-emergency-call-india",
     "Bystanders call your family without your PIN — fully no-unlock workflow.", 6, None),
    ("personal-bodyguard-app", "Personal Bodyguard App India 2026",
     "women", "Women Safety", "personal-bodyguard-app-india",
     "Free passive safety for working women — no panic button required.", 5, None),
    ("safety-app-for-night-shift", "Safety App for Night Shift Workers India 2026",
     "women", "Women Safety", "safety-app-night-shift-india",
     "Inactivity alert tuned to 8-hour shifts — auto-SOS if you don't check in.", 5, None),
    ("scan-to-call-emergency", "Scan to Call Emergency India 2026",
     "lock-screen", "Lock Screen", "scan-to-call-emergency-india",
     "How a lock-screen QR calls your family in 15 seconds — step-by-step.", 5, None),
    ("senior-citizen-safety-app", "Senior Citizen Safety App India 2026",
     "family", "Family & Senior", "senior-citizen-safety-app-india",
     "Passive protection for elderly parents — zero tech skills required.", 5, None),
    ("smart-sos-button", "Smart SOS Button India 2026",
     "sos", "Core SOS", "smart-sos-button-india",
     "Automatic alert without pressing anything — the case for passive-first design.", 5, None),
    ("solo-travel-safety-app", "Solo Travel Safety App India 2026",
     "crash-travel", "Crash & Travel", "solo-travel-safety-app-india",
     "Off-grid protection for Spiti, Ladakh and the Northeast — works on 2G.", 5, None),
    ("emergency-info-without-unlocking", "Emergency Info Without Unlocking Phone India",
     "lock-screen", "Lock Screen", "no-unlock-emergency-call-india",
     "End-to-end no-unlock setup — what bystanders see before your PIN.", 5, None),
    ("lock-screen-emergency-contact-app", "Lock Screen Emergency Contact App India 2026",
     "lock-screen", "Lock Screen", "lock-screen-emergency-qr-india",
     "One-tap call to Help Circle from a locked phone — for every Indian.", 5, None),
    ("lock-screen-medical-id-india", "Lock Screen Medical ID India 2026",
     "lock-screen", "Lock Screen", "medical-id-qr-code-india",
     "Blood group, allergies and meds — visible without ever unlocking.", 6, None),
    ("no-unlock-emergency-access-android", "No-Unlock Emergency Access Android India 2026",
     "lock-screen", "Lock Screen", "no-unlock-emergency-call-india",
     "Why HelpQR's QR wallpaper beats stock Android Emergency Information.", 5, None),
]

PILLAR_SLUGS = {"sos-app-india", "lock-screen-emergency-qr-india", "women-safety-app-2026"}

# Category counts
CAT_LABELS = {
    "all": "All",
    "lock-screen": "Lock Screen",
    "women": "Women Safety",
    "family": "Family & Senior",
    "sos": "Core SOS",
    "crash-travel": "Crash & Travel",
}
def cat_count(c):
    if c == "all": return len(POSTS)
    return sum(1 for p in POSTS if p[2] == c)

assert len(POSTS) == 40, f"expected 40 posts, got {len(POSTS)}"

# ── HTML PARTIALS ─────────────────────────────────────────────────────────────

HEAD_BLOCK = '''<!DOCTYPE html>
<html lang="en-IN">
<head><!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-TBTQS7KC');</script>
<!-- End Google Tag Manager -->
<meta charset="UTF-8"/>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png"/>
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"/>
<link rel="manifest" href="/manifest.json"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover"/>
<title>HelpQR Blog — Emergency Safety Tips &amp; Guides India 2026</title>
<meta name="description" content="40 expert guides on emergency safety apps, lock screen QR, SOS alerts, medical ID, women &amp; senior safety for every Indian family. HelpQR India 2026."/>
<meta name="robots" content="index,follow"/>
<link rel="canonical" href="https://helpqr.org/blog/"/>
<link rel="alternate" hreflang="en-IN" href="https://helpqr.org/blog/"/>
<link rel="alternate" hreflang="x-default" href="https://helpqr.org/blog/"/>
<meta name="theme-color" content="#8C0508"/>
<meta name="msapplication-navbutton-color" content="#8C0508"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta property="og:type" content="website"/>
<meta property="og:title" content="HelpQR Blog — Emergency Safety India 2026"/>
<meta property="og:description" content="40 guides on lock screen QR, SOS apps, medical ID and emergency safety for every Indian family."/>
<meta property="og:url" content="https://helpqr.org/blog/"/>
<meta property="og:image" content="https://helpqr-static.b-cdn.net/blogs_webp/sos-app-india.webp"/>
<meta property="og:site_name" content="Help QR"/>
<meta property="og:locale" content="en_IN"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:site" content="@helpqr_india"/>
<meta name="twitter:title" content="HelpQR Blog — Emergency Safety India 2026"/>
<meta name="twitter:description" content="40 guides on lock screen QR, SOS apps, medical ID and emergency safety for every Indian family."/>
<meta name="twitter:image" content="https://helpqr-static.b-cdn.net/blogs_webp/sos-app-india.webp"/>
<meta name="geo.region" content="IN"/>
<meta name="geo.placename" content="India"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&amp;family=DM+Serif+Display&amp;display=swap" rel="stylesheet"/>
'''

CSS_BLOCK = '''<style>
/* ══════════════════════════════════════════
   HEADER — unified (matches index.html)
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
   FOOTER — unified (matches index.html)
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
.heart{color:#ec3237}

/* ══════════════════════════════════════════
   PAGE BASE
══════════════════════════════════════════ */
:root{--p:#ec3237;--pd:#c0080d;--pl:#fdf1f1;--fg:#18191c;--bg:#f9f6f3;--card:#fff;--border:#f0e4e4;--muted:#5a5a5a;--r:.875rem;--sh:0 4px 24px -4px rgba(0,0,0,.08);}
*{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;-webkit-tap-highlight-color:transparent;}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--fg);-webkit-font-smoothing:antialiased;overflow-x:hidden;}
img{display:block;max-width:100%;height:auto}
a{text-decoration:none;color:inherit}
body{padding-top:0 !important;}

/* Blog Hero */
.blog-hero{
  background:linear-gradient(160deg,#8C0508 0%,#c0080d 60%,#3a0204 100%);
  padding:6.5rem 1.25rem 3rem;
  text-align:center;
  position:relative;
  overflow:hidden;
}
.blog-hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(255,255,255,.06) 0%,transparent 70%);}
.blog-hero h1{position:relative;font-family:'DM Serif Display',serif;font-size:clamp(1.7rem,5vw,3rem);color:#fff;margin-bottom:.6rem;text-shadow:0 2px 20px rgba(0,0,0,.35);}
.blog-hero p{position:relative;color:rgba(255,255,255,.86);font-size:1rem;max-width:560px;margin:0 auto;}
.hero-stats{position:relative;display:flex;justify-content:center;gap:2rem;margin-top:1.5rem;flex-wrap:wrap;}
.hero-stat{color:#fff;font-size:.78rem;letter-spacing:.04em;text-transform:uppercase;opacity:.78;display:inline-flex;align-items:center;gap:.4rem;}
.hero-stat strong{font-size:1rem;text-transform:none;letter-spacing:0;opacity:1;}
.hero-stat-dot{width:6px;height:6px;border-radius:50%;background:#fff;opacity:.5;}

/* Featured pillar */
.featured-wrap{max-width:1040px;margin:0 auto;padding:2.25rem 1.25rem .5rem;}
.featured-head{display:flex;align-items:center;gap:.6rem;margin-bottom:1rem;}
.featured-head h2{font-family:'DM Serif Display',serif;font-size:1.25rem;color:var(--fg);}
.featured-head .pulse{width:10px;height:10px;border-radius:50%;background:var(--p);box-shadow:0 0 0 4px rgba(236,50,55,.18);animation:pulse 2.2s ease-in-out infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(236,50,55,.18)}50%{box-shadow:0 0 0 8px rgba(236,50,55,.05)}}
.featured-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.1rem;}
.featured-card{position:relative;border-radius:var(--r);overflow:hidden;background:#18191c;color:#fff;min-height:230px;display:flex;flex-direction:column;justify-content:flex-end;box-shadow:0 8px 24px -8px rgba(0,0,0,.35);text-decoration:none;transition:transform .25s,box-shadow .25s;}
.featured-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1;transition:transform .5s;}
.featured-card::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(24,25,28,0) 30%,rgba(24,25,28,.88) 100%);z-index:2;}
.featured-card>*{position:relative;z-index:3;}
.featured-card:hover{transform:translateY(-5px);box-shadow:0 14px 32px -8px rgba(0,0,0,.45);}
.featured-card:hover img{transform:scale(1.06);}
.featured-card-body{padding:1.1rem 1.2rem 1.25rem;}
.featured-card-cat{display:inline-flex;align-items:center;gap:.35rem;font-size:.66rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#fff;background:rgba(255,255,255,.18);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);padding:.22rem .6rem;border-radius:99px;margin-bottom:.55rem;}
.featured-card-title{font-family:'DM Serif Display',serif;font-size:1.1rem;line-height:1.3;margin-bottom:.4rem;}
.featured-card-meta{font-size:.74rem;color:rgba(255,255,255,.8);display:flex;gap:.65rem;align-items:center;}
.pillar-pill{position:absolute;top:.75rem;right:.75rem;font-size:.62rem;font-weight:800;letter-spacing:.1em;padding:.25rem .55rem;border-radius:99px;background:#fff;color:var(--pd);box-shadow:0 2px 6px rgba(0,0,0,.18);z-index:3;}

/* Filter bar */
.cat-bar{display:flex;flex-wrap:wrap;gap:.5rem;justify-content:center;max-width:1040px;margin:1.5rem auto .25rem;padding:0 1.25rem;}
.cat-chip{font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:600;padding:.46rem 1rem;border-radius:99px;background:#fff;border:1px solid var(--border);color:#3a3a3a;cursor:pointer;transition:background .2s,color .2s,border-color .2s,transform .15s,box-shadow .2s;letter-spacing:.01em;display:inline-flex;align-items:center;gap:.4rem;}
.cat-chip:hover{background:var(--pl);color:var(--pd);border-color:#fcd5d6;}
.cat-chip[aria-pressed="true"]{background:var(--p);color:#fff;border-color:var(--p);transform:scale(1.02);box-shadow:0 4px 14px -4px rgba(236,50,55,.5);}
.cat-chip .num{opacity:.65;font-weight:500;font-size:.7rem;}
.cat-chip[aria-pressed="true"] .num{opacity:.9;}

/* Grid */
.blog-grid-wrap{max-width:1040px;margin:0 auto;padding:1.5rem 1.25rem 5rem;}
.grid-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem;}
.grid-header h2{font-family:'DM Serif Display',serif;font-size:1.4rem;}
.badge{background:var(--p);color:#fff;font-size:.72rem;font-weight:700;padding:.2rem .7rem;border-radius:99px;}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.25rem;}

.card{position:relative;display:flex;flex-direction:column;background:var(--card);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);text-decoration:none;color:inherit;transition:transform .25s,box-shadow .25s,border-color .25s;}
.card:hover{transform:translateY(-5px);box-shadow:0 14px 36px -6px rgba(236,50,55,.22);border-color:#fcd5d6;}
.card-img-wrap{position:relative;overflow:hidden;height:158px;background:#8C0508;}
.card-img-wrap img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s;}
.card:hover .card-img-wrap img{transform:scale(1.06);}

.card-flag{position:absolute;top:.65rem;left:.65rem;font-size:.62rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:.24rem .6rem;border-radius:99px;color:#fff;z-index:2;box-shadow:0 2px 8px rgba(0,0,0,.22);}
.card-flag.new{background:linear-gradient(135deg,#22c55e,#16a34a);}
.card-flag.pillar{background:linear-gradient(135deg,var(--p),var(--pd));}

.card-body{padding:1rem 1.1rem 1.2rem;flex:1;display:flex;flex-direction:column;gap:.45rem;}
.card-meta{display:flex;align-items:center;justify-content:space-between;gap:.5rem;}
.card-cat{font-size:.65rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--p);}
.card-time{font-size:.7rem;color:var(--muted);display:inline-flex;align-items:center;gap:.28rem;font-weight:500;}
.card-time svg{width:11px;height:11px;stroke:var(--muted);stroke-width:1.8;fill:none;}
.card-title{font-family:'DM Serif Display',serif;font-size:.98rem;line-height:1.32;color:var(--fg);}
.card-excerpt{font-size:.81rem;color:var(--muted);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.card-arrow{font-size:.78rem;font-weight:600;color:var(--p);margin-top:auto;display:inline-flex;align-items:center;gap:.3rem;transition:gap .2s,color .2s;}
.card:hover .card-arrow{gap:.55rem;color:var(--pd);}

.no-results{grid-column:1/-1;text-align:center;padding:3rem 1rem;color:var(--muted);font-size:.95rem;}
.hide{display:none!important;}

@media(max-width:480px){.cards{grid-template-columns:1fr;}.hero-stats{gap:.9rem;}}
</style>
'''

JSONLD_BLOCK = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"CollectionPage","name":"HelpQR Blog — Emergency Safety Tips & Guides India 2026","description":"40 expert guides on emergency safety apps, lock screen QR, SOS alerts, medical ID and more for every Indian family.","url":"https://helpqr.org/blog/","publisher":{"@type":"Organization","name":"Help QR","url":"https://helpqr.org","logo":{"@type":"ImageObject","url":"https://helpqr.org/assets/logo.webp","width":512,"height":512}},"inLanguage":"en-IN"}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://helpqr.org/"},{"@type":"ListItem","position":2,"name":"Blog","item":"https://helpqr.org/blog/"}]}
</script>
'''
# ItemList JSON-LD listing all 40 posts (added below dynamically)

SW_AND_HEAD_CLOSE = '''<script>if("serviceWorker" in navigator){window.addEventListener("load",function(){navigator.serviceWorker.register("/sw.js").catch(function(){});});}</script></head>
<noscript><iframe height="0" src="https://www.googletagmanager.com/ns.html?id=GTM-TBTQS7KC" style="display:none;visibility:hidden" width="0"></iframe></noscript>

<!-- HEADER — unified (matches index.html) -->
<header id="site-header" role="banner">
  <div class="header-inner">
    <a href="/" class="logo" aria-label="Help QR Home">
      <img src="/assets/logo.webp" alt="Help QR — Emergency Safety App" width="36" height="36" loading="eager" fetchpriority="high"/>
      <span class="logo-text">Help QR</span>
    </a>
    <a href="https://play.google.com/store/apps/details?id=com.qr.help.android" target="_blank" rel="noopener noreferrer" class="glass-btn" aria-label="Download Help QR on Google Play">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download Free
    </a>
  </div>
</header>
'''

FOOTER_BLOCK = '''<!-- FOOTER — unified (matches index.html) -->
<footer role="contentinfo">
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
</footer>
'''

SCRIPT_BLOCK = '''<script>
// Header scroll spy
(function(){
  var hdr=document.getElementById('site-header');
  if(!hdr) return;
  var ticking=false;
  window.addEventListener('scroll',function(){
    if(!ticking){
      requestAnimationFrame(function(){
        hdr.classList.toggle('scrolled',window.scrollY>50);
        ticking=false;
      });
      ticking=true;
    }
  },{passive:true});
})();
// Category filter
(function(){
  var chips=document.querySelectorAll('.cat-chip');
  var cards=document.querySelectorAll('.cards .card');
  var noResults=document.querySelector('.no-results');
  if(!chips.length||!cards.length) return;
  function setActive(active){
    chips.forEach(function(c){c.setAttribute('aria-pressed',c===active?'true':'false');});
    var cat=active.getAttribute('data-cat');
    var shown=0;
    cards.forEach(function(card){
      var match=(cat==='all')||(card.getAttribute('data-cat')===cat);
      card.classList.toggle('hide',!match);
      if(match) shown++;
    });
    if(noResults) noResults.classList.toggle('hide',shown>0);
    try{
      var url=new URL(window.location.href);
      if(cat==='all'){url.searchParams.delete('cat');}else{url.searchParams.set('cat',cat);}
      history.replaceState(null,'',url.toString());
    }catch(e){}
  }
  chips.forEach(function(c){c.addEventListener('click',function(){setActive(c);window.scrollTo({top:document.querySelector('.blog-grid-wrap').offsetTop-60,behavior:'smooth'});});});
  // Honour ?cat= deep-links
  try{
    var pre=new URL(window.location.href).searchParams.get('cat');
    if(pre){var match=document.querySelector('.cat-chip[data-cat="'+pre+'"]');if(match) setActive(match);}
  }catch(e){}
})();
</script>
'''

CLOCK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'

# ── HTML BUILDERS ─────────────────────────────────────────────────────────────

def featured_card_html(p):
    slug, title, cat, cat_label, img, excerpt, mins, _flag = p
    return (
        f'    <a class="featured-card" href="/blog/{slug}" aria-label="{title}">\n'
        f'      <img src="{CDN}/{img}.webp" alt="{title} — HelpQR India" loading="eager" fetchpriority="high" width="600" height="380"/>\n'
        f'      <span class="pillar-pill">★ Pillar</span>\n'
        f'      <div class="featured-card-body">\n'
        f'        <span class="featured-card-cat">{cat_label}</span>\n'
        f'        <h3 class="featured-card-title">{title}</h3>\n'
        f'        <div class="featured-card-meta">{CLOCK_SVG}<span>{mins} min read</span><span aria-hidden="true">·</span><span>{excerpt[:60]}{"…" if len(excerpt)>60 else ""}</span></div>\n'
        f'      </div>\n'
        f'    </a>\n'
    )

def card_html(p):
    slug, title, cat, cat_label, img, excerpt, mins, flag = p
    flag_html = ''
    if flag == 'NEW':
        flag_html = '<span class="card-flag new">New</span>'
    elif flag == 'PILLAR':
        flag_html = '<span class="card-flag pillar">Pillar</span>'
    return (
        f'    <a class="card" href="/blog/{slug}" data-cat="{cat}" aria-label="{title}">\n'
        f'      <div class="card-img-wrap">\n'
        f'        <img src="{CDN}/{img}.webp" alt="{title} — HelpQR India" loading="lazy" width="400" height="210"/>\n'
        f'        {flag_html}\n'
        f'      </div>\n'
        f'      <div class="card-body">\n'
        f'        <div class="card-meta">\n'
        f'          <span class="card-cat">{cat_label}</span>\n'
        f'          <span class="card-time" aria-label="Reading time">{CLOCK_SVG}<span>{mins} min read</span></span>\n'
        f'        </div>\n'
        f'        <h3 class="card-title">{title}</h3>\n'
        f'        <p class="card-excerpt">{excerpt}</p>\n'
        f'        <span class="card-arrow">Read guide <span aria-hidden="true">→</span></span>\n'
        f'      </div>\n'
        f'    </a>\n'
    )

def itemlist_jsonld():
    items = []
    for i, p in enumerate(POSTS, start=1):
        slug, title = p[0], p[1]
        items.append({"@type":"ListItem","position":i,"url":f"https://helpqr.org/blog/{slug}","name":title})
    obj = {"@context":"https://schema.org","@type":"ItemList","itemListElement":items}
    return '<script type="application/ld+json">\n' + json.dumps(obj, separators=(",",":"), ensure_ascii=False) + '\n</script>\n'

def build():
    pillars = [p for p in POSTS if p[7] == 'PILLAR']
    chips = ''.join(
        f'  <button type="button" class="cat-chip" data-cat="{code}" aria-pressed="{"true" if code=="all" else "false"}">{label}<span class="num">({cat_count(code)})</span></button>\n'
        for code, label in CAT_LABELS.items()
    )
    featured = ''.join(featured_card_html(p) for p in pillars)
    cards = ''.join(card_html(p) for p in POSTS)

    body = (
        '<div class="blog-hero">\n'
        '  <h1>Emergency Safety Blog</h1>\n'
        '  <p>40 expert guides on lock-screen QR, SOS apps, medical ID &amp; family safety — for every Indian household.</p>\n'
        '  <div class="hero-stats" aria-label="Blog stats">\n'
        '    <span class="hero-stat"><strong>40</strong> guides</span>\n'
        '    <span class="hero-stat-dot" aria-hidden="true"></span>\n'
        '    <span class="hero-stat"><strong>Updated</strong> 2026</span>\n'
        '    <span class="hero-stat-dot" aria-hidden="true"></span>\n'
        '    <span class="hero-stat"><strong>100% Free</strong></span>\n'
        '  </div>\n'
        '</div>\n\n'
        '<section class="featured-wrap" aria-labelledby="featured-heading">\n'
        '  <div class="featured-head">\n'
        '    <span class="pulse" aria-hidden="true"></span>\n'
        '    <h2 id="featured-heading">Featured pillar guides</h2>\n'
        '  </div>\n'
        '  <div class="featured-grid">\n'
        f'{featured}'
        '  </div>\n'
        '</section>\n\n'
        '<nav class="cat-bar" aria-label="Filter by category">\n'
        f'{chips}'
        '</nav>\n\n'
        '<div class="blog-grid-wrap">\n'
        '  <div class="grid-header">\n'
        '    <h2>All Articles</h2>\n'
        '    <span class="badge">40 Guides</span>\n'
        '  </div>\n'
        '  <div class="cards">\n'
        f'{cards}'
        '    <p class="no-results hide">No guides in this category yet — try another filter.</p>\n'
        '  </div>\n'
        '</div>\n'
    )

    html = (
        HEAD_BLOCK
        + CSS_BLOCK
        + JSONLD_BLOCK
        + itemlist_jsonld()
        + SW_AND_HEAD_CLOSE
        + '\n' + body + '\n'
        + FOOTER_BLOCK
        + '\n' + SCRIPT_BLOCK
        + '</body>\n</html>\n'
    )
    return html

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blog', 'index.html')
    html = build()
    with open(out, 'w', encoding='utf-8', newline='') as fh:
        fh.write(html)
    print(f'wrote {out}  ({len(html):,} bytes, {len(POSTS)} posts, {len(CAT_LABELS)-1} categories)')
