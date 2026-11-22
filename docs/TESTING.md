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
| `orbittip.py` | Right-click info in orbit (3 checks): every kind of orbit object records a hitbox; a real `contextmenu` on each (fired in the same frame, as they move) opens a tip naming it and its builder; empty space gives nothing and the ground keeps the close-zoom rule. Expect `3/3 passed`. |
| `bodies.py` | Solar-system close-ups (11 checks): every body can be picked; real left clicks zoom in on Mars (bases, colony), the Sun (swarm shares) and Jupiter (ice moon owner); a click, Esc or the wheel zoom out (the wheel without changing the zoom); an unvisited world says so; Earth goes back to the globe; with a space tool selected a click places it instead. Writes `bodies_mars.png`, `bodies_sun.png`. Expect `11/11 passed`. |
| `aginat.py [N] [SECONDS]` | "Real data" for the AGI epic: natural worlds; per world the highest meter, when 30/60/90 were crossed (age, character), futures begun and endings, answers to AI pressure by character, wars begun (noisy: compare two runs of the old build too) and the average meter per character at the end. Worlds that end in the takeover run on for `CARE` seconds (env, default 400): holdouts, joins, wars touching peoples in care, tech gained in care, stability, forest share and pollution before/after. Each machine uprising is listed (when, whose machines, outcome, war length, peoples overrun, largest share of their continent), and every merge (when, old character, age, during the Waking Machines or not). `GAME=/path/to/old/index.html` runs another build for comparison. |
| `endnat.py [N] [SECONDS]` | "Real data" for the END epic: N natural worlds run SECONDS of sim time through endings and new cycles, counting tipping points, sea rise, nuclear wars and winters, bunkers, plagues, cycles, ruins, scavenging, dead worlds and a save round-trip. Example: `python endnat.py 12 3000`. |
| `balance.py` | 18 worlds to their endings: which futures start, which endings happen. |
| `realrun.py N SECONDS summary.js` | **"Real data" runs**: N natural worlds (nothing forced) to SECONDS after the first people reaches space, then runs `summary.js` in each and prints the result. The `sum_*.js` files are summaries for bases, resources, energy, megastructures, colonies, ships, space events, the Three-Sun story, and everything at once (`sum_all.js`, which also checks a save round-trip). |
| `shot_space.py AFTER ZOOMS OUT.png` | Grows a natural world, then screenshots it at the given zoom levels into one composite image. |

Example: `python realrun.py 12 900 sum_all.js`.

## Habits

- Test the feature directly, then with natural worlds, then the regression set; run several scripts in parallel.
- Long runs may open an epilogue; scripts that click must close it (`run2.py` installs an interval that does).
- Clicking toolbox tabs scrolls the page: `scrollTo(0, 0)` before clicking the map.
- Compare saved state after `sanitizeWorld` allowing for rounding (numbers are rounded to 4 decimals) and for missing keys becoming `null`/`false`.
