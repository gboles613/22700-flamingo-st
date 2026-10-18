#!/usr/bin/env python3
"""Builds the 22700 Flamingo St listing site from _build/config.json + _build/photos.json."""
import json, re, html, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
C = json.load(open(os.path.join(HERE, "config.json")))
PHOTOS = json.load(open(os.path.join(HERE, "photos.json")))

def is_ph(v): return bool(re.search(r"\{\{.*\}\}|_PLACEHOLDER", str(v)))
def esc(s): return html.escape(str(s), quote=True)
def show(key, suffix=""):
    v = C[key]
    if is_ph(v): return f'<span class="ph" title="Placeholder: fill in _build/config.json">{esc(v)}</span>'
    return esc(v) + suffix

ADDR = "22700 Flamingo St"; CITY = "Woodland Hills"; ST = "CA"; ZIP = "91364"
FULL_ADDR = f"{ADDR}, {CITY}, {ST} {ZIP}"
LAT, LNG = 34.148, -118.621
SITE = C["SITE_URL"].rstrip("/") + "/"
EMAIL = C["EMAIL"]
SUBJ = "Inquiry: 22700 Flamingo St, Woodland Hills rental"
MAILTO = f"mailto:{EMAIL}?subject=" + SUBJ.replace(" ", "%20").replace(",", "%2C").replace(":", "%3A")
TEL = "tel:" + C["PHONE_TEL"]
SQFT_NUM = int(C["SQFT"].replace(",", "")) if not is_ph(C["SQFT"]) else None

# --- text bits (only known facts) ---
spec_bits = []
for k, label in (("BEDS", "bed"), ("BATHS", "bath")):
    if not is_ph(C[k]): spec_bits.append(f"{C[k]} {label}")
spec_bits.append(f"{C['SQFT']} sq ft")
spec_line = ", ".join(spec_bits)
rent_txt = "" if is_ph(C["RENT"]) else f" for {C['RENT']}/month"
TITLE = f"For Rent: {FULL_ADDR} | Renovated {spec_line} Home"
DESC = (f"Renovated two-story {spec_line} single-family home for lease{rent_txt} at {FULL_ADDR}: vaulted ceilings, "
        "quartz kitchen, gas fireplace, huge primary walk-in closet, balcony with 180° views, covered patio and private yard. "
        "5% broker commission offered. Video tour, photos and contact.")

FEATURES = [
  ("Interior", ["Living room with vaulted, beamed ceilings and floor-to-ceiling windows",
                "Gas fireplace with stacked-stone surround",
                "Separate den with sliding doors to the covered patio",
                "Dining room off the kitchen",
                "Wood-look plank flooring and recessed lighting throughout",
                "Nest smart thermostat"]),
  ("Kitchen", ["Large quartz countertop and white shaker cabinetry",
               "Stainless steel French-door refrigerator, gas cooktop and wall oven",
               "Pull-out, soft-close drawers",
               "Subway-tile backsplash"]),
  ("Bedrooms & Baths", ["Spacious primary suite with two walk-in closets, including one very large closet",
                        "Primary bath with soaking tub and glass shower with built-in bench",
                        "Downstairs bedroom that also works as a home office",
                        "Upstairs bathroom with double vanity",
                        "Bedroom with vaulted ceiling and balcony access",
                        "Walk-in linen closet"]),
  ("Outdoor & Utility", ["Furnished balcony with sweeping 180° views",
                         "Covered patio, outdoor dining area and grassy backyard",
                         "Landscaped front yard and attached garage",
                         "Laundry room with LG front-load washer and dryer on storage pedestals"]),
]

# --- JSON-LD ---
img_urls = [SITE + f"images/full/{p['file']}.webp" for p in PHOTOS]
residence = {
  "@type": "SingleFamilyResidence", "@id": SITE + "#residence",
  "name": f"{ADDR}, {CITY}",
  "address": {"@type": "PostalAddress", "streetAddress": ADDR, "addressLocality": CITY,
              "addressRegion": ST, "postalCode": ZIP, "addressCountry": "US"},
  "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LNG},
  "image": [SITE + "images/full/01-front-of-house.jpg"] + img_urls[1:12],
  "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in
                     ["Vaulted ceilings", "Gas fireplace", "Quartz countertops", "Walk-in closets", "Balcony with views",
                      "Covered patio", "Private backyard", "In-unit laundry (washer and dryer)", "Smart thermostat", "Attached garage"]],
}
if SQFT_NUM: residence["floorSize"] = {"@type": "QuantitativeValue", "value": SQFT_NUM, "unitCode": "FTK", "unitText": "sq ft"}
if not is_ph(C["BEDS"]): residence["numberOfBedrooms"] = C["BEDS"]
if not is_ph(C["BATHS"]): residence["numberOfBathroomsTotal"] = C["BATHS"]
if not is_ph(C["PETS"]): residence["petsAllowed"] = C["PETS"]

offer = {"@type": "Offer", "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut",
         "itemOffered": {"@id": SITE + "#residence"}, "areaServed": f"{CITY}, {ST}",
         "seller": {"@type": "Person", "name": C["CONTACT_NAME"], "telephone": C["PHONE_TEL"]}}
if not is_ph(EMAIL): offer["seller"]["email"] = EMAIL
if not is_ph(C["RENT"]):
    amt = re.sub(r"[^\d.]", "", C["RENT"])
    offer["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": amt, "priceCurrency": "USD", "unitCode": "MON", "unitText": "month"}
    offer["price"] = amt; offer["priceCurrency"] = "USD"
if not is_ph(C["AVAILABLE_DATE"]): offer["availabilityStarts"] = C["AVAILABLE_DATE"]

listing = {"@type": "RealEstateListing", "@id": SITE + "#listing", "url": SITE, "name": TITLE, "description": DESC,
           "datePosted": C["LAST_UPDATED"], "image": SITE + "images/og-image.jpg",
           "about": {"@id": SITE + "#residence"}, "offers": offer,
           "mainEntity": {"@id": SITE + "#residence"}}
video = {"@type": "VideoObject", "@id": SITE + "#video",
         "name": f"Video tour: {FULL_ADDR} rental home",
         "description": f"2.5-minute walkthrough video tour of the renovated home for lease at {FULL_ADDR}.",
         "thumbnailUrl": [SITE + "media/video-poster-kitchen.jpg"], "uploadDate": "2026-10-18",
         "duration": "PT2M30S", "contentUrl": SITE + "media/22700-flamingo-st-video-tour.mp4",
         "embedUrl": SITE + "#video-tour"}
webpage = {"@type": "WebPage", "@id": SITE + "#webpage", "url": SITE, "name": TITLE, "description": DESC,
           "inLanguage": "en-US", "dateModified": C["LAST_UPDATED"], "primaryImageOfPage": SITE + "images/og-image.jpg",
           "mainEntity": {"@id": SITE + "#listing"}, "video": {"@id": SITE + "#video"}}
JSONLD = json.dumps({"@context": "https://schema.org", "@graph": [webpage, listing, residence, video]}, indent=1, ensure_ascii=False)

# --- gallery ---
gal = []
for i, p in enumerate(PHOTOS):
    eager = i < 4
    gal.append(f'''<figure class="g-item{' g-wide' if i == 0 else ''}">
  <a href="images/full/{p['file']}.webp" data-idx="{i}" data-caption="{esc(p['caption'])}">
    <img src="images/thumb/{p['file']}.webp" width="{p['tw']}" height="{p['th']}" alt="{esc(p['alt'])}" {'loading="eager"' if eager else 'loading="lazy"'} decoding="async">
  </a>
  <figcaption>{esc(p['caption'])}</figcaption>
</figure>''')
GALLERY = "\n".join(gal)
FEAT_HTML = "\n".join(f'<div class="feat"><h3>{esc(h)}</h3><ul>' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul></div>" for h, items in FEATURES)

email_label = esc(EMAIL)
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(TITLE)}</title>
<meta name="description" content="{esc(DESC)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-video-preview:-1">
<link rel="canonical" href="{esc(SITE)}">
<meta name="geo.region" content="US-CA">
<meta name="geo.placename" content="{CITY}, Los Angeles, California">
<meta name="geo.position" content="{LAT};{LNG}">
<meta name="ICBM" content="{LAT}, {LNG}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(FULL_ADDR)}">
<meta property="og:title" content="{esc(TITLE)}">
<meta property="og:description" content="{esc(DESC)}">
<meta property="og:url" content="{esc(SITE)}">
<meta property="og:image" content="{esc(SITE)}images/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Front of the renovated home at {esc(FULL_ADDR)}">
<meta property="og:video" content="{esc(SITE)}media/22700-flamingo-st-video-tour.mp4">
<meta property="og:video:type" content="video/mp4">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(TITLE)}">
<meta name="twitter:description" content="{esc(DESC)}">
<meta name="twitter:image" content="{esc(SITE)}images/og-image.jpg">
<meta name="twitter:image:alt" content="Front of the renovated home at {esc(FULL_ADDR)}">
<meta name="theme-color" content="#1c2430">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" as="image" href="images/full/01-front-of-house.webp" fetchpriority="high">
<link rel="alternate" type="text/plain" href="llms.txt" title="LLM-readable listing summary">
<link rel="stylesheet" href="styles.css">
<script type="application/ld+json">
{JSONLD}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="banner" role="note"><strong>{esc(C["BROKER_COMMISSION"])}</strong><span class="banner-sep" aria-hidden="true">·</span><a href="{TEL}">Brokers call {esc(C["PHONE_DISPLAY"])}</a></div>
<header class="topbar">
  <nav aria-label="Sections">
    <a href="#video-tour">Video</a><a href="#photos">Photos</a><a href="#details">Details</a><a href="#neighborhood">Area</a><a class="nav-cta" href="#contact">Contact</a>
  </nav>
</header>

<main id="main">
<section class="hero" id="top" aria-labelledby="h1">
  <picture>
    <img class="hero-img" src="images/full/01-front-of-house.webp" width="{PHOTOS[0]['w']}" height="{PHOTOS[0]['h']}" alt="{esc(PHOTOS[0]['alt'])}" fetchpriority="high" decoding="async">
  </picture>
  <div class="hero-shade"></div>
  <div class="price-badge" id="price-badge" role="note" aria-label="Price reduced $600: was $8,095, now $7,495"><span class="pb-top">Reduced $600</span><span class="pb-sub">was <s>$8,095</s>, now <b>$7,495</b></span></div>
  <div class="hero-inner">
    <p class="eyebrow">For Lease · Single-Family Home</p>
    <h1 id="h1">{ADDR}<span>{CITY}, {ST} {ZIP}</span></h1>
    <p class="hero-sub">A completely renovated two-story home with vaulted ceilings, a balcony with 180° views and a private backyard in the hills of Woodland Hills.</p>
    <ul class="stats" aria-label="Key facts">
      <li><b>{show("RENT")}</b><span>per month</span></li>
      <li><b>{show("BEDS")}</b><span>bedrooms</span></li>
      <li><b>{show("BATHS")}</b><span>bathrooms</span></li>
      <li><b>{show("SQFT")}</b><span>sq ft</span></li>
    </ul>
    <div class="cta-row">
      <a class="btn btn-gold" href="{TEL}">Call {esc(C["PHONE_DISPLAY"])}</a>
      <a class="btn btn-ghost" href="{esc(MAILTO)}">Email about this home</a>
    </div>
  </div>
</section>

<section class="section" id="video-tour" aria-labelledby="video-h">
  <div class="wrap">
    <p class="kicker">Video tour</p>
    <h2 id="video-h">Walk through the home</h2>
    <div class="video-frame">
      <video controls playsinline preload="metadata" poster="media/video-poster-kitchen.jpg" width="1920" height="1080" aria-label="Video walkthrough tour of {esc(FULL_ADDR)}">
        <source src="media/22700-flamingo-st-video-tour.mp4" type="video/mp4">
        Your browser can't play this video. <a href="media/22700-flamingo-st-video-tour.mp4">Download the video tour</a>.
      </video>
    </div>
    <p class="muted">A 2.5-minute walkthrough of {FULL_ADDR}.</p>
  </div>
</section>

<section class="section alt" id="photos" aria-labelledby="photos-h">
  <div class="wrap">
    <p class="kicker">Photo gallery</p>
    <h2 id="photos-h">{len(PHOTOS)} photos, inside and out</h2>
    <p class="muted">Tap any photo to view it full size.</p>
    <div class="gallery">
{GALLERY}
    </div>
  </div>
</section>

<section class="section" id="details" aria-labelledby="details-h">
  <div class="wrap">
    <p class="kicker">Property details</p>
    <h2 id="details-h">Lease details &amp; features</h2>
    <dl class="facts">
      <div><dt>Address</dt><dd>{FULL_ADDR}</dd></div>
      <div><dt>Property type</dt><dd>Single-family home, two stories</dd></div>
      <div><dt>Monthly rent</dt><dd>{show("RENT")}</dd></div>
      <div><dt>Bedrooms</dt><dd>{show("BEDS")}</dd></div>
      <div><dt>Bathrooms</dt><dd>{show("BATHS")}</dd></div>
      <div><dt>Living area</dt><dd>{show("SQFT")} sq ft</dd></div>
      <div><dt>Available</dt><dd>{show("AVAILABLE_DATE")}</dd></div>
      <div><dt>Furnished</dt><dd>{show("FURNISHED")}</dd></div>
      <div><dt>Broker compensation</dt><dd>{esc(C["BROKER_COMMISSION"])}</dd></div>
    </dl>
    <div class="features">
{FEAT_HTML}
    </div>
  </div>
</section>

<section class="section alt" id="neighborhood" aria-labelledby="hood-h">
  <div class="wrap narrow">
    <p class="kicker">The neighborhood</p>
    <h2 id="hood-h">Living in Woodland Hills</h2>
    <p>Woodland Hills is a residential neighborhood of the City of Los Angeles in the southwest San Fernando Valley. Its southern edge rises into the Santa Monica Mountains, where tree-lined hillside streets like Flamingo Street sit above the valley floor.</p>
    <p>Everyday conveniences are close by: restaurants and shops along Ventura Boulevard, the Warner Center business district, and shopping and dining at Westfield Topanga and The Village. The US-101 Ventura Freeway connects Woodland Hills to the rest of Los Angeles and to Calabasas and the Conejo Valley, and Topanga State Park and other Santa Monica Mountains open space are nearby for hiking.</p>
  </div>
</section>

<section class="section contact" id="contact" aria-labelledby="contact-h">
  <div class="wrap narrow center">
    <p class="kicker light">Schedule a showing</p>
    <h2 id="contact-h">Interested in {ADDR}?</h2>
    <p>Call or email {esc(C["CONTACT_NAME"])} to ask questions or book a tour. Brokers: {esc(C["BROKER_COMMISSION"].replace(" Offered", " offered"))}.</p>
    <div class="cta-row center">
      <a class="btn btn-gold" href="{TEL}">Call {esc(C["PHONE_DISPLAY"])}</a>
      <a class="btn btn-ghost" href="{esc(MAILTO)}">Email {email_label}</a>
    </div>
  </div>
</section>
</main>

<footer class="footer">
  <div class="wrap">
    <address>
      <strong>{FULL_ADDR}</strong><br>
      Single-family home for lease · Contact {esc(C["CONTACT_NAME"])} · <a href="{TEL}">{esc(C["PHONE_DISPLAY"])}</a> · <a href="{esc(MAILTO)}">{email_label}</a>
    </address>
    <p class="fine">Information is deemed reliable but not guaranteed; prospective tenants should verify all details. Equal Housing Opportunity. Last updated {esc(C["LAST_UPDATED"])}.</p>
  </div>
</footer>

<div class="mcta" aria-hidden="false"><a href="{TEL}">Call</a><a href="{esc(MAILTO)}">Email</a></div>

<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Photo viewer" hidden>
  <button class="lb-close" aria-label="Close">&times;</button>
  <button class="lb-prev" aria-label="Previous photo">&#8249;</button>
  <figure><img id="lb-img" alt=""><figcaption id="lb-cap"></figcaption></figure>
  <button class="lb-next" aria-label="Next photo">&#8250;</button>
</div>
<script src="hero.js"></script>
<script src="lightbox.js" defer></script>
</body>
</html>
'''
open(os.path.join(ROOT, "index.html"), "w").write(page)

# --- llms.txt ---
def val(k): return C[k] if not is_ph(C[k]) else "Not yet published (contact owner)"
feat_txt = "\n".join(f"- {x}" for _, items in FEATURES for x in items)
llms = f"""# {FULL_ADDR}: single-family home for lease

> Completely renovated two-story single-family rental home at {FULL_ADDR} (Woodland Hills, Los Angeles, California). 2,638 sq ft of living space. 5% broker commission offered (up to a 1-year lease). Contact {C['CONTACT_NAME']} at {C['PHONE_DISPLAY']}.

## Key facts
- Address: {FULL_ADDR}
- Neighborhood: Woodland Hills, City of Los Angeles, southwest San Fernando Valley
- Coordinates: {LAT}, {LNG}
- Property type: Single-family home, two stories
- Living area: {C['SQFT']} sq ft
- Monthly rent: {val('RENT')}
- Bedrooms: {val('BEDS')}
- Bathrooms: {val('BATHS')}
- Available: {val('AVAILABLE_DATE')}
- Furnished: {val('FURNISHED')}
- Broker compensation: {C['BROKER_COMMISSION']}
- Contact: {C['CONTACT_NAME']}, phone {C['PHONE_DISPLAY']} ({C['PHONE_TEL']}), email {EMAIL}

## Features
{feat_txt}

## Media
- Listing page: {SITE}
- Video tour (2.5 min, MP4): {SITE}media/22700-flamingo-st-video-tour.mp4
- Photo gallery ({len(PHOTOS)} photos): {SITE}#photos

## Last updated
{C['LAST_UPDATED']}
"""
open(os.path.join(ROOT, "llms.txt"), "w").write(llms)

open(os.path.join(ROOT, "robots.txt"), "w").write(f"""User-agent: *
Allow: /
Disallow: /_build/

# AI crawlers are welcome
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /

Sitemap: {SITE}sitemap.xml
""")

imgs = "\n".join(f"""    <image:image><image:loc>{SITE}images/full/{p['file']}.webp</image:loc></image:image>""" for p in PHOTOS)
open(os.path.join(ROOT, "sitemap.xml"), "w").write(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
  <url>
    <loc>{SITE}</loc>
    <lastmod>{C['LAST_UPDATED']}</lastmod>
{imgs}
    <video:video>
      <video:thumbnail_loc>{SITE}media/video-poster-kitchen.jpg</video:thumbnail_loc>
      <video:title>Video tour: {FULL_ADDR} rental home</video:title>
      <video:description>2.5-minute walkthrough video tour of the renovated home for lease at {FULL_ADDR}.</video:description>
      <video:content_loc>{SITE}media/22700-flamingo-st-video-tour.mp4</video:content_loc>
      <video:duration>150</video:duration>
    </video:video>
  </url>
</urlset>
""")
print("built; placeholders remaining:", sorted({k for k, v in C.items() if not k.startswith('_') and is_ph(v)}))
