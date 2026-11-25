# Wiki Trails

Discover geotagged Wikipedia articles around a town, landmark or chosen coordinates, then build a private walking list. Live application: https://coolcode.ca/wikitrails/.

<!-- coolcode:guide -->
Choose Halifax waterfront or search for another starting point, then increase the radius if few articles appear. Distances are straight-line measurements to article coordinates, not walking directions; save interesting places and check access before visiting.
Use **Pictures of this place** on a result to open Commons Lens with that record’s coordinates prefilled. Commons Lens waits for you to submit before requesting media.
<!-- /coolcode:guide -->

## Features

- Search any town, neighbourhood or landmark with a geotagged Wikipedia article; coordinate entry works anywhere.
- Grouped starting places across British Columbia, Nova Scotia, Atlantic Canada, Ontario/Quebec, the Prairies and the North; the three quick-start buttons remain compact.
- Optional geolocation, adjustable 500 m–10 km search radius, local text filter and interactive map.
- Wikipedia extracts, available article thumbnails, article links and exact source revision links.
- Private saved places, reordering, removal and JSON export. Up to 200 saved places.
- Responsive list and map; the list remains useful if map tiles fail.

## Sources and meanings

The app calls the public [Wikipedia Action API](https://www.mediawiki.org/wiki/API:Geosearch) directly using `origin=*`. There is no API key, proxy or scheduled dataset. The selected language defaults to English. Results contain a maximum of 40 geotagged articles within the requested radius; this is not a complete inventory of places. The visible retrieval time records the request, not the article's publication date. Article revision links identify the excerpt's source.

Article text is attributed to Wikipedia contributors under CC BY-SA 4.0. Image licensing is available through the article's image page. Map tiles are from OpenStreetMap, with attribution. Leaflet 1.9.4 is vendored under its BSD-2-Clause licence in `web/vendor/`.

## Privacy

Place searches and chosen coordinates go to Wikipedia. The browser contacts OpenStreetMap for map tiles and Wikimedia for thumbnails. Location permission is requested only after pressing the location button. Saved places are stored under `coolcode:wikitrails:saved`; no accounts or server-side history. Clear the list to remove it, or export a portable copy. This shares an origin with other CoolCode tools but uses a separate storage key.

## Expand or customize

Edit `web/config.json`. Add any preset using `{ "name": "Dartmouth waterfront", "lat": 44.6654, "lon": -63.5684, "group": "Nova Scotia", "quick": false }`. The selector groups every configured place; set `quick: true` only for a few frequently used starting points. Presets are conveniences, not an allowlist. Visitors can always search or enter other valid coordinates. Change `language` to a supported two- or three-letter Wikipedia language code, `default_radius_m` between 100 and 10000, or `result_limit` between 1 and 50.

Push the configuration change to `main`; the normal Pages workflow builds and publishes it. No data-refresh workflow, schedule guard, collector heartbeat or API secret is required. Existing saved lists remain usable after presets change. Users can switch language by changing config in their own deployment.

## Development and publication

Requires Python 3.12+ and Node 24+ for checks. No runtime package installation.

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

`dist/` is generated and ignored. GitHub Actions `Browser tool · Check and publish` checks the application and browser flow, then deploys successful main builds via Pages. PRs do not deploy. The repository must use Pages → GitHub Actions. Keep the project URL `/wikitrails/`; do not add a CNAME.

For browser checks, install `tests/browser-requirements.txt` and Chromium in CI and run `python3 tests/browser_smoke.py`. The test intercepts Wikipedia responses and map tiles, exercising the actual UI deterministically without relying on source availability.

## Integration scope

This round only changes the ten new repositories. `tool.json` is ready for the catalogue; shared hub registration and watchdog inventory changes are coordinated outside this repository. The app itself has no periodic collection and needs no Worker handler.
