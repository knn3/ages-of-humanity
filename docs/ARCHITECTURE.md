# Architecture

Everything lives in `index.html`: a `<style>` block, the page markup, and one `<script>` holding a single IIFE. Sections are marked with comments like `/* ---------- fates: what the future becomes ---------- */`; find them with `grep -n "^/\* ----------" index.html`.

## Section map (in file order)

| Section | What it holds |
|---|---|
| utilities | `clamp`, `lerp`, `rand`, `pick`, `h01` (hash noise), `esc`, `$`, formatting (`fmtYear`, `fmtPop`, `fmtSpan`) |
| world constants | `WORLD_W` 12000, `STEP`, `BASE_Y`, `SEA0`, `MAXERA` 14, `FUTURE` 11, `BUCKET` (era → text bucket 0–6), `SPACE_PACE`, zoom constants (`ZMIN` .00002, `ZSYS` .012, `ZMAX` 2.4, `ZBEND0` .5, `ZGLOBE` .06), `ATMO` shells, `smooth`, `bendOf` |
| the ages | `ERAS` (15 ages: name, start/end years, dates, carrying capacity K, key resource, milestone text, `future` flag), `KEYNAME`, `KEYERA`, `TRAITS` (Warlike, Mercantile, Devout, Curious), `GOVT`, `NAMES`, `COLORS` |
| elements | `ELEMENTS` (land elements; `dep` = underground deposit; `sea`; `space` = Moon/belt/giant) |
| events | `EVENTS` (id, name, glyph, cat, scope global/target/land, minEra, special, fx), `CATS`, `STRESS`, `RESP` (reactions with per-bucket texts), `LETH`, `SIZES` (building sizes), `PLAN` (buildings per age), `LIT`, `CLOTH` |
| state | `W` (the world), `V` (view/visual state), `UI`, `CUSTOM` (player-made elements/events/rules) |
| terrain | `genBase` (4 landmasses), `recomputeTerrain`, `gy(x)` ground height, `seaY()`, `V.lands` |
| lookups / text | `alive()`, `civById`, `civAt(x)`, `names(c)`, `fillT` (`{Civ}`, `{civ}`, `{other}` templates), `txt(arr, era)` (bucketed text) |
| making the world | `freshWorld`, `newWorld(seed)` |
| simulation | `updateCiv` (food, pop, tech via `addTech`, stability), `eraUp`, territories, `contact`, wars, relations, reactions (`queueReaction`), keys and trade (`resOf`, `hasKey`) |
| events (logic) | `applyEvent` → `applyEvent0` (counts player acts), `SPECIAL` handlers, `randomEvent` |
| rules | `checkRules`, `fireRule`, `CONDS`, `ruleLabel` |
| nature | 120-cell grid `W.nat {f, w, s, fish}`, land-use policies (exploit/balance/protect), extinctions |
| main step | `step(dt)`: fixed substeps; calls civ updates, wars, nature, rules, `fateTick` and `spaceTick` once per sim second |
| space | Moon/Mars bases (`BODY`, `W.bases`), space resources (`W.spaceRes`, `claimSpace`), energy scale (`energyOf`, Kardashev), megastructures (`W.dyson`, `W.megas`), colonies → off-world peoples (`W.colonies`), generation ships (`W.ships`, `W.stars`, `XSTARS`) |
| Three-Sun Signal | `W.tb` state; stances, physics lock (`tbLocked`), strategist, probe, deterrence, broadcast/strike, occupation |
| end of the world | `RISE_WAIT`, ruins (`W.ruins`, `leaveRuins`, `ruinBonus`, `drawRuins`, `RUIN_KIND`), bunkers (`crisisCiv`), nuclear winter (`startWinter`, `endWinter`, `winterK`), runaway warming (`tipWarming`, `W.hot`, `W.seaRise` → `seaY()`), engineered plague (`startPandemic`, `pandemicTick`), machine autonomy (`c.mach`, `c.machSaid`, `MACH_TRAIT`, `MACH_CAP`, `machRate`, `machAdd`, `machTick` called from `updateCiv`; fed into `fateCtx` as `mach`/`machAvg`), seed vaults and libraries (`keepersOf`, `keepStart` used by `riseAgain`, `keepEl`, `keepersTick`, `keepersLine`), supervolcano and asteroid (`startSupervolcano`, `worldWinter`, `startAsteroid`, `deflectChance`, `tryDeflect`, `rockTick`, `rockImpact`, `ROCK_ETA`), `endTick` (once per sim second, before `fateTick`), `crisisChips`, `crisisMeta` |
| fates | `FATES` (13 futures with `drive`, `span`, texts, optional hooks `begin/tick/finish/clock/manual/endingId/endText`), `FATE_UI`, `ENDINGS` (15), `fateTick`, `startFate`, `endFate`, `reachEnding`, epilogue (`showEpilogue`), `riseAgain` (new cycle) |
| layout / buildings | settlements laid out per civ in `c._.items` (`{t, x, w, h, base}`), painters per building type (`P.<type>(b, c)`) |
| rendering | flat view (`drawWorld` into an offscreen canvas, night/lights passes), overlay labels, `drawOverlay`, minimap |
| atmosphere / globe | bent strip rendering, globe face from a texture, atmosphere shells, `drawSpaceBackdrop` (Sun, Moon), `drawSpaceExtras`/`drawOrbit` (satellites, stations, elevators, cylinders, debris), `drawSystem` (planets, swarm, resources), `drawGalaxy` |
| interface | tool tabs, info popovers (`infoContent`, `showPop`), map info box (`tipTarget`, `tipBody`, right click), futures panel (`updateFutures`), people cards, ribbon, workshop, rules tab, modal, saving, input, boot |

## Key state

`W` (serialised by `serialize()`, everything except keys named `_`):
- `seed, simTime, year, civs[], elements[], craters[], wars[], chron[] (≤260), nat, pollution, tempShift, ruleState, nextId`
- futures: `fates {edgeT, p, bias, active[], done[], hist[], cycle, ended, endY, arks}`, `acts` (player interventions), `sig` (alien signal), `nukeT`, `lastWarT`, `warCount`
- space: `bases[], spaceRes[], colonies[], ships[], stars[], dyson {by, total, mark}, megas[], debris, kessler, flareUntil`
- Three-Sun: `tb {t0, lock, probe, stances, strat, plan, chosen, fleet, ark, deter, strikeT, occ, endAs, endTxt}`
- end of the world: `ruins[] {x, w, h, era, k: tower|dome|wall|road, t0, by}` (≤48), `winter {t0, until, full, kind: nuke|ash|impact, pop0}`, `rock {t0, eta, x, size, seen, tries, next, name}`, `rockCycle`, `svCycle`, `hot {on, acc, t0, nextMig}`, `seaRise` (0–34 px, raises `seaY()`), `pandemic {t0, src, inf{id: level}, at{id: t}, rec[], pop0}`, `plagueCycle`; `fates.riseAt` (auto new cycle) and `fates.ruined`
- per civ: `bunker` 0–1, `closed` (borders closed until), `scav` / `drownSaid` (cycle in which it was said), `fallEra` (age reached when the world fell, used for the next start); transient `c._.scav`, `c._.drown`, `c._.sick`

A civ `c`: `id, name, color, trait, govt, era, tech, pop, food, stability, military, culture, x, l, r, reached{era: year}, threshold, kLevel, policy`, plus transient `c._` (layout items, agents, ships, planes, train, nature summary, megaK…).

`V`: camera (`cam`, `camY`, `zoom`, `s` scale, `b` bend 0–1, `cx/cy` globe centre, `Rb`), time `t`, day `dayT`, effects arrays, `picks` (clickable objects drawn this frame), `labs` (label info-button positions).

## Zoom chain

ground (flat strip) → `ZBEND0` .5 the strip starts to bend → `ZGLOBE` .06 full globe with atmosphere shells → `ZSYS` .012 solar system fades in (`sysK`, camera drifts to the Sun via `sysC`) → .00025 galaxy fades in (`galK`, camera drifts to the galactic centre via `galC`) → `ZMIN` .00002.

## Saves

- `localStorage`: `aoh.world.v2` (autosave), `aoh.save.v2` (Save button), `aoh.custom.v1` (workshop creations, `CUSTOM.v = 2`).
- World codes: base64 of `{world, custom}`.
- Load path: `sanitizeWorld(d)` rebuilds a clean world from untrusted data, clamping every number, whitelisting ids/kinds, and defaulting missing new fields (old saves stay valid).

## Debug hook

`window.__aoh` exposes `W` (getter), `V`, `UI`, `setZoom, enterFS, exitFS, toggleTools, step, applyEvent, findEvent, EVENTS, render, newWorld, serialize, loadWorld, sanitizeWorld, setTool, worldClick, placeElement, nuclearWar, tipTarget, W2S, S2W, gy, FATES, fateDrives, fateTick, startFate, endFate, tbChoose, tbBroadcast, energyOf, foundBase, spaceTick, placeSpace, reachEnding, showEpilogue, riseAgain, ENDINGS, updateUI, machRate, machAdd, machTick, fateCtx, keepersOf, keepStart, keepEl, keepersTick, startSupervolcano, startAsteroid, tryDeflect, deflectChance, rockImpact, leaveRuins, ruinBonus, startWinter, startPandemic, tipWarming, endTick, winterK, crisisMeta, temp, seaY`.

## Adding a future's real content (pattern used by the Three-Sun Signal)

1. Give the entry in `FATES` hooks: `begin()` (set up `W.<state>`), `tick(a, dt)` (runs every sim second while active), `finish(outcome)` (clean up, reveal), optional `clock(a)` for the panel label, `manual: true` if it ends itself, `endingId()` / `endText()` to choose the ending.
2. Add endings to `ENDINGS` (`kind`: doom / end / goal; `scene` CSS filter; `text`).
3. Add any hand-triggered events to `EVENTS` (category `Futures` or `Space`) with a `SPECIAL` handler and an `EVINFO` text.
4. Save the new state in `sanitizeWorld`; show it on cards (`st.push(chip)`) and in `tipBody` info rows.
5. Test with natural runs (`tests/realrun.py`) and by hand.
