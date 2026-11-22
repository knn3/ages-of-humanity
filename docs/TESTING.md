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
| `balance.py` | 18 worlds to their endings: which futures start, which endings happen. |
| `realrun.py N SECONDS summary.js` | **"Real data" runs**: N natural worlds (nothing forced) to SECONDS after the first people reaches space, then runs `summary.js` in each and prints the result. The `sum_*.js` files are summaries for bases, resources, energy, megastructures, colonies, ships, space events, the Three-Sun story, and everything at once (`sum_all.js`, which also checks a save round-trip). |
| `shot_space.py AFTER ZOOMS OUT.png` | Grows a natural world, then screenshots it at the given zoom levels into one composite image. |

Example: `python realrun.py 12 900 sum_all.js`.

## Habits

- Test the feature directly, then with natural worlds, then the regression set; run several scripts in parallel.
- Long runs may open an epilogue; scripts that click must close it (`run2.py` installs an interval that does).
- Clicking toolbox tabs scrolls the page: `scrollTo(0, 0)` before clicking the map.
- Compare saved state after `sanitizeWorld` allowing for rounding (numbers are rounded to 4 decimals) and for missing keys becoming `null`/`false`.
