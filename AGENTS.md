# CoolCode browser tool conventions

- Keep app source in `web/`, build code in `scripts/`, and meaningful tests in `tests/`.
  Never commit `dist/`. Do not add dependencies without a concrete application need.
- Run `scripts/init.py` as documented in README, then replace the example UI,
  behaviour, tests and privacy text. Review all fields in `tool.json`.
- Build for expandable personal use: keep watchlists, preset queries, source
  selections and tunable limits in a documented configuration file. Defaults are
  starting points; accept arbitrary valid visitor input when the source permits it.
  Derive counts, filters and validation from actual data, never a starter list's
  length. Test adding an item beyond the defaults. Preserve earlier captures with
  different coverage and clearly show the selected capture date. The README must
  explain the exact edit, refresh and publication steps under Expand or customize.
- Keep `access: "browser"` for the usable web tool. Selecting local files is not
  installation. The hub renders its standard access label from this field.
- Keep assets and imports relative so the app works at `/<repo>/`. Do not add a
  CNAME or claim the hub's domain. Link home to `https://coolcode.ca/`.
- Keep transformations separate from DOM code. Render untrusted input through
  textContent/value, not innerHTML. Never embed API secrets.
- State which inputs leave the browser. Do not retain pasted text or uploads by
  default. Namespace preferences as `coolcode:<tool-id>:<key>`; paths share storage.
- Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests -v`,
  and `python3 scripts/build.py`. Preview `dist/` using a local HTTP server.
- Update `tests/browser_smoke.py` when replacing the sample UI. CI runs it with
  Chromium; `tests/browser-requirements.txt` contains the test-only dependency.
- The default build is offline. Add data refresh only when needed, with validation
  and visible source/build dates. Failed refreshes must not replace good deployments.
- When adding scheduled collection, retain workflow_dispatch and generate the
  separate allowlisted guard with scripts/add_schedule_guard.py as documented.
  Include every scheduled collector; update the list on workflow renames/removals.
  Register the collector and freshness expectations with the independent Linux
  scheduler. The guard is an interim mitigation, not proof that data is fresh.
- PRs check/build; successful `main` builds deploy. The template repo skips deployment.
- Once deployed, copy the reviewed `tool.json` record into `data/tools.json` in
  `jsdyer/jsdyer.github.io`. Don't register the starter itself as a finished tool.
- For changes to inputs, coverage, date meanings or results, update the tool README
  alongside the implementation. Its marked `coolcode:guide` excerpt supplies
  the extra practical detail in the hub README. Only the short source sentence
  belongs in the homepage record. Import the note with `scripts/sync_guides.py
  --tool TOOL_ID` in the hub before regenerating its README.

- For EVERY addition, update, rename or removal, follow the mandatory lifecycle at
  https://github.com/jsdyer/jsdyer.github.io/blob/main/docs/tool-lifecycle.md.
  Consider all affected catalogue/README notes, audit coverage, generated Worker and
  deployment receipt, watchdog targets/probes/App permissions, guard and sitemap.
  Do not report a release complete with these integrations left implicit.

- Give the page a concise task-based search title using `init.py --search-title`; keep
  the application name on the page. Retain the build-time search metadata helper,
  choose an accurate app category, and derive any Dataset metadata from real inputs.
  Never substitute a build timestamp for a source edition or fabricate ratings.
