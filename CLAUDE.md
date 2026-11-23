# CLAUDE.md — Ages of Humanity

Guide for any AI agent (or person) picking up this project. Read this first, then `docs/ARCHITECTURE.md` before touching code.

## What this is

**Ages of Humanity** is a 2D side-view simulation game of human civilisation, from the Prehistoric Age to the Galactic Age and beyond. Peoples ("civs") live on a long wrapping strip of land with oceans between continents. The player places elements (rivers, herds, ores…) and triggers events (droughts, plagues, inventors…), and each people reacts according to its age and character. Zooming out bends the strip into a globe, then the solar system, then the galaxy. After the Future Age, "futures" (fates) take over: alien contact, collapse, AGI, the Garden, and more, each with its own ending.

- The **whole game is one file**: `index.html` (~4,100 lines; HTML, CSS and JS inline, no build step, no dependencies except Google Fonts).
- The **published copy** lives as a Claude artifact (see Links). `index.html` here is the latest source.
- The **ticket tracker** is `tickets/tickets.xlsx` (exported from the live tracker sheet).

## Links

| What | Where |
|---|---|
| Source repo (GitHub, private) | https://github.com/knn3/ages-of-humanity — branch `main` |
| Public website (GitHub Pages) | https://knn3.github.io/ages-of-humanity/ — auto-deployed by `.github/workflows/pages.yml` on every push to `main` that changes `index.html`; only `index.html` is published |
| Game (live, private to the owner) | https://claude.ai/artifact/GFVdMcCoxYPrnCGJKF9ihw — artifact slug `7b7f2273-f157-4b5c-be02-fa01dc003a2a` |
| Ticket tracker (live Claude Sheet) | https://claude.ai/artifact/PgA5BkivNH23ZXc4Ezp73S — slug `b7a0a602-065d-4887-b6d5-d498c12aaead`, workbook node `521317ae-02b8` |
| Offline tickets | `tickets/tickets.xlsx` (Tickets + Epics sheets), `tickets/tickets.csv` |

The artifacts belong to the owner's claude.ai account. An agent with the claude-artifacts tools can republish the game with `publish_files` (slug above, mode `patch`, `as: index.html`, base_version from `get_artifact`). The tracker is edited through the Claude Docs connector (`update` with `applyEdits`; see that connector's `topic.sheets`). If you have neither, work on `index.html` here and the xlsx.

## How to run

Open `index.html` in any modern browser (double-click it). Everything else is in the README.

## Repository layout

```
index.html            the game (single file)
CLAUDE.md             this guide
README.md             human-facing overview and controls
docs/ARCHITECTURE.md  code map: sections, state, systems, rendering, saves
docs/GAMEPLAY.md      design: ages, peoples, events, futures, endings, space
docs/TESTING.md       how the headless tests work and how to run them
docs/CHANGELOG.md     what was built, in order, with the user's requests
docs/WORKFLOW.md      how work has been done here (tickets, testing, publishing, user preferences)
tickets/tickets.xlsx  all 71 tickets + epic progress (formulas)
tickets/tickets.csv   same tickets as CSV
tests/                Python + Playwright test scripts and JS summaries (endworld.py, end06.py, end07.py, endnat.py for the END epic; agi01.py…agi06.py, aginat.py for AGI; sv01.py…sv03.py, sum_chronlinks.js, sum_vlog.js, shot_lens.py for Star voyages)
```

## Status (as of 2026-11-23)

- **Done:** Foundation epic (FND-01…07), Into space (SPC-01…10), Three-Body (TB-01…08), End of the world epic (END-01…07: new cycles, ruins, nuclear winter, runaway warming, engineered plague, supervolcano and asteroid, seed vaults and libraries), AGI takeover epic (AGI-01…06: machine autonomy meter, reactions by character, caretaker ending, war against the machines, the merge, the grey spread), SV-01…04 (chronicle ship lines open a one-ship lens or the settled world's close-up; ship on its way; voyage log and ship card; named new worlds), plus many UI requests (see CHANGELOG).
- **In progress:** FND-08 balance pass (re-run after the remaining epics).
- **Next:** Star voyages (SV-05…07: follow generation ships to new worlds in a neighbourhood lens; P2, ahead of Wandering Earth), then Wandering Earth, Ascension, Garden, Great Silence, Simulation reveal, Speciation, Long Night, Geoengineering, First contact, Immortality. All are in `tickets/tickets.xlsx` with descriptions, "done when" criteria and dependencies.
- Several later epics already have placeholder behaviour: each future starts, has reactions, a countdown and an ending text (see `FATES` and `ENDINGS`). Their tickets replace placeholders with real content, the way TB-01…08 did for the Three-Sun Signal.

## Hard rules and user preferences (keep these)

1. **One file.** Keep the game in `index.html`. No frameworks, no build, no external JS. Fonts: Marcellus (display), IBM Plex Sans Condensed (body), IBM Plex Mono (numbers). Theme: dark obsidian and bronze; futures use violet `#a593f2`.
2. **Do not change the map type.** The user explicitly decided to keep the side-view strip + globe + solar system + galaxy zoom chain as it is.
3. **Info on the map opens with a RIGHT CLICK** (contextmenu), only when zoomed in close (`TIP_ZOOM = 1.3`) — except objects in orbit, which can be right-clicked on the curved globe/orbit views (`orbitTarget`); in the solar-system view a LEFT click on the Sun, the Moon or a planet opens its close-up (`focusBody`) — only on an actual object (building, person, vehicle, animal, tree, ship, element, deposit…). No hover tags. Left click places tools / selects / drags.
4. **City info** is the small **i** button on each city label (click, not hover).
5. **Toolbox and panels:** show only the name, with an **i** button for details (hover or click shows a popover).
6. **Normal cursor** on the map (no grab hand, no crosshair).
7. **British spelling** ("civilisation", "colour"). Plain, readable chronicle text. Real names from the Three-Body Problem / Wandering Earth are NOT used in-game: use original names (e.g. the Hevari of Hevar) and mark tickets "inspired by".
8. **Every saved structure must be sanitised on load** (`sanitizeWorld`, `sanitizeFates`, `sanitizeCustom`). Old saves must keep loading.
9. **Expose new systems on `window.__aoh`** so the headless tests can drive them.
10. After finishing a ticket: test (including **"real data" runs**: natural worlds with nothing forced), publish, set the ticket to Done in the tracker, and report briefly. The user often asks for several tickets in one go ("run the next 5 jobs and test").

## Working loop that has worked well

1. Mark the ticket **In progress** (tracker column E).
2. Read the relevant code section (use the `/* ---------- section ---------- */` markers; `grep -n`).
3. Patch `index.html` with small, exact string replacements (a Python script that asserts each `old` string occurs exactly once is safest; the file is large).
4. Syntax check: `node -e "const s=require('fs').readFileSync('index.html','utf8'); new Function(s.match(/<script>([\s\S]*)<\/script>/)[1])"`.
5. Test: a focused script for the feature, `tests/realrun.py` with a summary JS for natural worlds, then the regression set (`tests/run2.py`, `tests/saves.py`, …). See `docs/TESTING.md`.
6. Look at the result visually once (a composite screenshot) when the change is visual.
7. Publish, update the tracker, report what was built, what the tests showed, and what's next.

## Gotchas

- `W.chron` is capped at 260 entries: counting chronicle lines in long runs undercounts. `W.hist` holds the whole story (oldest first, up to 5,000 lines).
- `#modal` is moved into `#stage` while in full screen (`openModal`), so dialogs show in real full screen.
- The clock runs fast in the Galactic Age (~30 years per sim second), so countdowns read in thousands of years late in the game.
- An epilogue modal can open at any time in long runs and block clicks; tests close it (see `run2.py`).
- Clicking toolbox tabs scrolls the page; tests that click the map should `scrollTo(0,0)` first.
- `STARS` is the backdrop star list; voyage targets are `XSTARS`.
- Futures marked `manual: true` (the Three-Sun Signal) end themselves; the engine does not end them by span.
- In the solar/galaxy views (`sysK() > .3`) labels, floaters, war badges and orbit clutter are hidden on purpose.
