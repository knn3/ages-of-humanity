# Testing

The game has no unit tests; it is tested headlessly with **Python + Playwright**, driving the page through the debug hook `window.__aoh` and through real clicks.

## Setup

```bash
pip install playwright pillow
python -m playwright install chromium        # or point CHROME at an installed Chrome:
export CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS example
cd tests
python run2.py
```

Every script finds the game as `../index.html` and blocks network requests (fonts fall back), so runs are offline and deterministic enough. Scripts print results and `no errors` when the page raised no errors.

## The scripts

| Script | Checks |
|---|---|
| `run2.py` | **Main regression**: long simulation, all events, workshop, rules, save/load. Prints `events ok N` and `no errors`. |
| `saves.py` | 9 save checks: save button + reload, world codes, old saves, garbage data, endings, second cycle, autosave. Expect 9 PASS. |
| `rules.py` | Future and energy rule conditions and "end a future" actions via the Rules tab. |
| `futev.py`, `futpanel.py`, `fates.py` | Futures events, the Futures panel (countdowns, info, fold, full screen), which futures different worlds reach. |
| `epi.py` | A doom ending, the epilogue, "Begin again from the ruins", the galactic ending. |
| `ages.py` | Worlds run through the Planetary, Stellar and Galactic ages; old saves move past the old edge. |
| `orbit.py`, `system.py` | Orbit layer and debris cascade; zooming out to the solar system. |
| `spaceplace.py`, `spaceev.py` | Placing space resources; the five space events. |
| `tbui.py`, `tbend.py` | Three-Sun Signal: choosing the strategist, stances, save mid-story; broadcast, strike and the flattening. |
| `clicktip3.py`, `picks.py`, `labinfo.py`, `hover4.py`, `hover5.py` | Right-click info on people, buildings, elements, every drawn object; label **i** buttons; no info when zoomed out; underground deposits. |
| `perf_fuzz.py` | Draw time at 11 zoom levels on a late-game world, then 260 random actions (clicks, right clicks, drags, wheel, tools, keys). |
| `endworld.py` | End of the world (29 checks): auto new cycle and cycle counter, dead world, ruins (kinds, scavenging bonus, fading, right click), nuclear winter with and without bunkers, bunkers dug near midnight, one-sided strike, runaway warming (tipping, sea rise, drowned coasts, refugees, stopped by dimming the Sun), engineered plague (spread, open vs closed borders, can end a cycle), saves and old/garbage saves. Expect `29/29 passed`. |
| `end06.py` | Supervolcano and asteroid (18 checks): eruption, caldera, volcanic winter, near vs far losses, ending vs survival, countdown, strike on time, crater, big impact ends the world, deflection succeeds and fails and is likelier for advanced peoples, unseen without telescopes, saves. Expect `18/18 passed`. |
| `end07.py` | Seed vaults and libraries (14 checks): toolbox, placing, start age with nothing / vault / library / both after a Future Age and a Classical Age fall, the age at the fall is remembered and saved, peoples build them (more vaults under danger), right click, epilogue "Kept safe". Expect `14/14 passed`. |
| `agi01.py` | Machine autonomy (12 checks): none before the Information Age, rises faster in the Future Age, Curious fastest and Devout slowest, AI Awakening jump and speed-up, chronicle lines at 30/60/90, card row and chip, pushes the fate drive, save/sanitise, reset on a new cycle. Expect `12/12 passed`. |
| `agi02.py` | Reactions by character (8 checks): each character's own answer ~90%, what each answer does (with its chronicle line), a ban slows the meter, AI pressure arrives on its own (milestones, now and then, AI Awakening, the Waking Machines), the ban is saved and sanitised. Expect `8/8 passed`. |
| `agi03.py` | Caretaker ending (15 checks): the takeover and its chronicle lines, a Devout holdout stays outside, then 300 s under the caretakers: no war even when ordered, no progress, stability/food up and armies down, cut forests regrow and pollution falls, holdouts still progress, caretaker chronicle lines, a holdout gives in at 60, no reactions in care, its own epilogue rows, card chip, save/sanitise (old saves that ended in the takeover get caretakers), new world without. Writes `agi03_care.png`. Expect `15/15 passed`. |
| `agi04.py` | War against the machines (17 checks): the uprising (a new people, own looks, war with the makers, human wars set aside, makers weakened), no births / no food / no progress / no choices, other humans join, The Iron Dominion with its epilogue rows, the humans win (ban), the power cut on a long war, the future waits for the war, rising on its own (Warlike most, never without the fate), the player's event, no plague, card, rust on a new cycle, save/sanitise. Writes `agi04_machines.png`. Expect `17/17 passed`. |
| `agi05.py` | The merge (10 checks): merging as an answer to AI pressure (only during the Waking Machines, meter 85+, no ban; 1,000 draws per character: Curious most, Devout never), a people merges by its own choice (character becomes Merged), merged vs human over 30 s (progress multiplier, births, stability, no AI pressure, no uprising), neural city, card, the Merge event (and the uprising refused), never born merged, a new cycle restores the old character, save/sanitise. Writes `agi05_merged.png`. Expect `10/10 passed`. |
| `landmark.py` | Town landmarks (2 checks): across 40 worlds every machine people has its machine core and every human town of every age has its landmark (the old build missed 4 cores and 18 landmarks). `GAME=` runs another build. Expect `2/2 passed`. |
| `galaxy.py` | The Milky Way (8 checks): the Sun ~26,000 ly out, between the Sagittarius and Perseus arms; a ~30,000 ly bar with its near end ~27° from the Sun; major arms start at the bar's ends; no text drawn on the canvas at galaxy zoom; no solar-system cluster (planets, Moon, claims) and nothing piled on the Sun at galaxy scale; zoomed out the centre is in the middle with the Sun below; clicking the Sun and the centre. Writes `galaxy_*.png`. Expect `8/8 passed`. |
| `history.py` | The whole chronicle (12 checks): natural runs to the end keep every line (800–1,400, past the chronicle's 260); See all shows them newest first; filters, search, no-match note, oldest first, Close; opens from the panel and from the full-screen feed (inside the stage); a new world starts again; saved and loaded; bad lines cleaned; old saves start from the chronicle; capped at 5,000 with a count of faded lines. Expect `12/12 passed`. |
| `closeupfs.py` | Close-ups in full screen and in the page at 1600×900, 1300×850, a tall 1000×1094 and a narrow 700×900 (16 checks), for the Sun, Jupiter, Saturn, Mars, the Moon and Venus. Wide views: the body is huge (radius over 40% of the height, or of 60% of the width on tall screens; Saturn 32%), centred on screen, wholly left of the text. Narrow views: the body on screen above the card, clear of the overlays. Always: the text is on screen and clear of the hint bar, chronicle feed and altitude box. The old build failed 7. Expect `16/16 passed`. |
| `fshint.py` | Full-screen hint (3 checks): the page view keeps the hint bar; full screen leaves out the general hint and the chronicle feed drops into its place; a tool still shows its own hint. Expect `3/3 passed`. |
| `minimap.py` | Strip map (6 checks, page and full screen): shown on the ground and close in, hidden on the globe, in the solar system and the galaxy, back on the ground; hiding it does not move the map. Expect `6/6 passed`. |
| `fslog.py` | Full-screen chronicle toggle (6 checks): hidden outside full screen; shows the latest lines under a Chronicle toggle; folds away; counts new lines while folded; remembered after a reload; opens again. Writes `fslog_open.png`, `fslog_closed.png`. Expect `6/6 passed`. |
| `orbittip.py` | Right-click info in space (7 checks): every kind of orbit object records a hitbox; a real `contextmenu` on each (fired in the same frame, as they move) opens a tip naming it and its builder, which is still open 1.5 s later; with the game running the tip stays open and closes when you zoom back to the ground; a left click on a claim in the solar system, and right clicks on a ship and a star colony in the galaxy, open tips that stay; empty space gives nothing and the ground keeps the close-zoom rule. Expect `7/7 passed`. |
| `bodies.py` | Solar-system close-ups (11 checks): every body can be picked; real left clicks zoom in on Mars (bases, colony), the Sun (swarm shares) and Jupiter (ice moon owner); a click, Esc or the wheel zoom out (the wheel without changing the zoom); an unvisited world says so; Earth goes back to the globe; with a space tool selected a click places it instead. Also checks that the text card never covers the body, its rings, swarm or moons, nor the hint bar or altitude box, at 2000, 1300, 900 and 640 px wide. Writes `bodies_mars.png`, `bodies_sun.png` and wide/narrow shots. Expect `12/12 passed`. |
| `aginat.py [N] [SECONDS]` | "Real data" for the AGI epic: natural worlds; per world the highest meter, when 30/60/90 were crossed (age, character), futures begun and endings, answers to AI pressure by character, wars begun (noisy: compare two runs of the old build too) and the average meter per character at the end. Worlds that end in the takeover run on for `CARE` seconds (env, default 400): holdouts, joins, wars touching peoples in care, tech gained in care, stability, forest share and pollution before/after. Each machine uprising is listed (when, whose machines, outcome, war length, peoples overrun, largest share of their continent), and every merge (when, old character, age, during the Waking Machines or not). `GAME=/path/to/old/index.html` runs another build for comparison. |
| `endnat.py [N] [SECONDS]` | "Real data" for the END epic: N natural worlds run SECONDS of sim time through endings and new cycles, counting tipping points, sea rise, nuclear wars and winters, bunkers, plagues, cycles, ruins, scavenging, dead worlds and a save round-trip. Example: `python endnat.py 12 3000`. |
| `balance.py` | 18 worlds to their endings: which futures start, which endings happen. |
| `realrun.py N SECONDS summary.js` | **"Real data" runs**: N natural worlds (nothing forced) to SECONDS after the first people reaches space, then runs `summary.js` in each and prints the result. The `sum_*.js` files are summaries for bases, resources, energy, megastructures, colonies, ships, space events, the Three-Sun story, and everything at once (`sum_all.js`, which also checks a save round-trip). |
| `shot_space.py AFTER ZOOMS OUT.png` | Grows a natural world, then screenshots it at the given zoom levels into one composite image. |

Example: `python realrun.py 12 900 sum_all.js`.

## Habits

- Test the feature directly, then with natural worlds, then the regression set: `bash tests/run_all.sh` runs every script, `JOBS` at a time (default 6). Launching all the browsers at once makes page loads time out, so re-run any failure on its own before believing it.
- Long runs may open an epilogue; scripts that click must close it (`run2.py` installs an interval that does).
- Clicking toolbox tabs scrolls the page: `scrollTo(0, 0)` before clicking the map.
- Compare saved state after `sanitizeWorld` allowing for rounding (numbers are rounded to 4 decimals) and for missing keys becoming `null`/`false`.
