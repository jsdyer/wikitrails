# CoolCode browser tool template

A starting point for independent tools at `coolcode.ca/<repo>/`: a working local-text
example, responsive UI, Python standard-library build, Node tests, PR checks and Pages
publication. No npm install is needed.

## Using the example

<!-- coolcode:guide -->
The first occurrence of each trimmed line keeps its place. Compare the output with the original text before copying the result.
<!-- /coolcode:guide -->

For a real tool, replace this paragraph with one or two plain-text sentences
about an example, a limit or how to interpret the results. Keep the source,
coverage, refresh behaviour and a worked example in this README as appropriate.
When updating a tool, revise any details its behaviour has changed and keep the
homepage's shorter data-source sentence in `tool.json` accurate.
The hub imports the marked note into the catalogue README.

## One-time template setup

Enable **Settings → General → Template repository** here. This repository does not
need Pages enabled: its workflow builds/tests but intentionally skips deployment.
New copies also skip deployment until `scripts/init.py` sets the tool ID to match
their repository name. This lets you create the repo before configuring Pages.

## Start a new tool

1. Select **Use this template → Create a new repository**, choose owner `jsdyer`,
   a unique lowercase name such as `my-tool`, and public visibility.
2. Clone the new repository. Use Python 3.12+ and Node 24+.
3. Set the identity, using a slug that matches the repository name:

```sh
python3 scripts/init.py my-tool --title "My Tool" --description "Describe what this tool does."
```

Review the category, tags and icon in `tool.json`. `access: "browser"` tells the main
catalogue that the tool works immediately without installation. `--owner` supports a different
GitHub owner, but only projects owned by `jsdyer` inherit the CoolCode domain.

4. Replace the example in `web/` and its tests. Update the privacy explanation,
   source attribution and README to describe the real tool.
5. Test and preview:

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/`. The example trims lines, skips blanks and removes exact
duplicates, preserving first-seen order and capitalization. It processes the text in tab memory. Update that explanation if your app behaves differently.

CI also tests the browser flow and mobile layout at a project subpath. Replace the
sample assertions in `tests/browser_smoke.py` when implementing your own UI. To run
that check locally (optional for ordinary preview):

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tests/browser-requirements.txt
python3 -m playwright install --with-deps chromium
python3 tests/browser_smoke.py
```

Playwright is a test-only dependency; the app and its static build do not use it.

## Expand or customize

Every implemented tool should replace this section with its actual configuration
path and a working example. A small `config.json` can hold default entities,
query presets, source choices and request limits. Those defaults should be useful
starting points, while visitors can enter other valid inputs whenever the source
supports them. Keep provider limits explicit and separate from the starter list.

Derive counts, filters and item validation from the current data. Do not require
exactly the initial number of items. Add a test that expands the configuration,
and keep historical captures readable when their coverage differs from today's
watchlist. Display the selected capture date accurately.

Document which changes need only a normal code push and which also need a data
refresh. Include the refresh command or exact GitHub workflow and input, followed
by the publication step. A successful code build need not mean a new collection
has been fetched. The starter itself has no external collection or refresh.

## Publish and register

When the actual tool is ready, in the **new tool repository** set **Settings → Pages → Build and deployment →
Source → GitHub Actions**. Push to `main`, or manually run **Browser tool · Check and
publish** after enabling Pages. If the initial deployment ran before Pages was enabled,
enable it and rerun. PRs only check/build and provide a downloadable preview artifact.

Keep `{{VISIT_COUNTER}}` in the page head and `{{ISSUE_LINK}}` in the footer when replacing the starter UI. The build enables these for initialized CoolCode repositories. The shared counter records aggregate opens on coolcode.ca by public tool ID. Toolbox inputs and URL parameters are excluded. The issue link opens a reporting form with the tool already selected.

Keep app-owned asset paths and module imports relative. Check `https://coolcode.ca/my-tool/`.
Do not add a CNAME or set `coolcode.ca` as this project's custom domain; the account
site supplies it. Only successful `main` builds deploy.

After verifying the app, copy the reviewed object from `tool.json` into `data/tools.json`
in [the main site](https://github.com/jsdyer/jsdyer.github.io). Each tool still builds
independently. The hub generates the visitor Worker ID list, watchdog targets and sitemap; deploy and verify the affected services before considering the release complete. Update the hub record when listing metadata changes; the hub is the
authority for discovery. Every change must follow the [mandatory lifecycle](https://github.com/jsdyer/jsdyer.github.io/blob/main/docs/tool-lifecycle.md). App-only changes may leave integrations unchanged, but this must be checked; documentation, source fields, schedules and registration changes also require the hub update.

The main site separates **Use in your browser** from **Install yourself**. An app
that asks for a file is still a browser tool. Standalone Linux packages should start
in their own repositories with their own build/release workflow, rather than copying
this browser-only scaffold. Their hub record uses `access: "install"`, links to an
installation guide, and includes `requirements`.

## Files

| Path | Purpose |
| --- | --- |
| `tool.json` | Page metadata and a ready-to-copy catalogue record |
| `web/` | HTML, responsive CSS, DOM interactions and separate model logic |
| `scripts/build.py` | Escape metadata and build `web/` into `dist/` |
| `scripts/init.py` | Set a new project's identity |
| `scripts/add_schedule_guard.py` | Add an opt-in guard for explicitly selected scheduled collectors |
| `tests/` | Application and builder tests |
| `.github/workflows/pages.yml` | Check PRs and publish successful main builds |
| `AGENTS.md` | Instructions for future coding work |

Namespace optional storage as `coolcode:<tool-id>:<key>`; CoolCode paths share a
browser origin. Don't save pasted text/uploads by default. Document external APIs
and send only the information needed for the selected action. Never embed secrets.

Scheduled refresh is opt-in. Validate source data before deploying, display its date,
and preserve the last good deployment on failure. Public-repository schedules can
stop after 60 days without repository activity.

When adding a collector with `on.schedule`, also keep `workflow_dispatch` available
for the independent Linux server scheduler. Generate a separate schedule guard,
listing every scheduled collector in the repository:

```sh
python3 scripts/add_schedule_guard.py --repository jsdyer/my-tool .github/workflows/pages.yml
```

Replace the repository and workflow paths with the real values. Review the generated
allowlist, commit `.github/workflows/schedule-guard.yml`, and verify its first push
run. Re-run the command with the complete list when adding, renaming or removing a
collector. The guard runs weekly, independently of collector failures, and calls
GitHub's enable-workflow API for those paths and itself. It restores workflows
disabled for inactivity and preserves manually disabled workflows. It does not
fetch data, create dummy commits or change source/check timestamps.

This is an interim mitigation: GitHub does not document active-workflow renewal as
a permanent exemption, and scheduled runs can be delayed or dropped. Register the
collector and its freshness expectations in the independent server scheduler too.
Document its real data check, collection and publication steps in the tool README.
The starter has no scheduled collector and therefore ships no recurring guard job.

Templates don't propagate future edits automatically. Adopt fixes explicitly and
consider a versioned reusable workflow once several tools confirm the shared process.
Choose and add the intended software license before distributing a new project.

## Search metadata

Initialize the page title with a concise task phrase, while keeping the creative
app name in `--title`:

```sh
python3 scripts/init.py line-cleaner --title "Line Cleaner" --description "Trim lines and remove exact duplicates in your browser." --search-title "Trim Lines & Remove Duplicates"
```

The build adds static `WebApplication` JSON-LD, a free CAD offer and social metadata.
For initialized jsdyer tools it also adds the canonical CoolCode URL. Forks and the
uninitialized template do not claim a CoolCode canonical. Review the application
category in `scripts/build.py` when adapting the tool; the starter is a utility.
Do not invent ratings or reviews. Search markup does not guarantee a rich result.

For a saved public dataset, pass Dataset objects to `add_search_metadata` from the
app builder, with actual source attribution, licence, coverage and download URLs.
Derive counts and dates from the same snapshot used by the app and show those details
on the page. Keep source edition, retrieval and page-build time distinct. Omit an
unknown source modification date instead of setting it to the current build time.
Read the hub's `docs/search-discovery.md` for the release checklist.
