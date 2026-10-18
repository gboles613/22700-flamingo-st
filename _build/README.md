# 22700 Flamingo listing site
Static site; no framework. To change details, edit `_build/config.json`, then run `python3 _build/build.py` from the site root.
Placeholders: SITE_URL (final https URL, e.g. https://<user>.github.io/<repo>/), EMAIL, RENT, BEDS, BATHS, AVAILABLE_DATE, PETS, FURNISHED.
Values still in {{ }} show as yellow placeholders on the page and are omitted from the JSON-LD.
Deploy: push this folder's contents to a GitHub repo and enable Pages (root). `_build/` is disallowed in robots.txt.
