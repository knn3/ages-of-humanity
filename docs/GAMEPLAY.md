# Gameplay and design

## The ages (15)

| # | Age | Dates | Key to enter it |
|---|---|---|---|
| I | Prehistoric | 200,000–10,000 BCE | — |
| II | Stone | 10,000–4500 BCE | fertile land (or a river) |
| III | Copper | 4500–3300 BCE | copper |
| IV | Bronze | 3300–1200 BCE | tin |
| V | Iron | 1200–500 BCE | iron |
| VI | Classical | 500 BCE–500 CE | gold |
| VII | Medieval | 500–1400 CE | standing forest |
| VIII | Renaissance | 1400–1700 CE | a coast |
| IX | Industrial | 1700–1900 CE | coal |
| X | Modern | 1900–1970 CE | oil (uranium gives the bomb) |
| XI | Information | 1970–2030 CE | silicon |
| XII | Future | 2030–2100 CE | lithium |
| XIII | Planetary | 2100–2400 CE | — |
| XIV | Stellar | 2400–3000 CE | helium-3 |
| XV | Galactic | 3000 CE onward | asteroid metals or an ice moon |

(Exact keys and dates: `ERAS`, `KEYERA` in `index.html`.) A people that holds the key for its next age advances faster; neighbours it can reach may trade for it. The world clock follows the real timeline; peoples run ahead or fall behind it. The space ages pass more slowly (`SPACE_PACE`).

## Peoples

Up to 8 peoples on 4 landmasses separated by sea. Each has a **character** (Warlike, Mercantile, Devout, Curious) that weights how it responds to stresses (food, loss, threat, unrest, boom, ecology…), a government, and land-use policy (exploit, balance, protect). Wars come from adjacency, sea contact and tension; world wars and nuclear war exist. Off-world colonies can become peoples of their own (cards under "Off-world peoples").

## The player's tools

- **Elements** (left click on land): river, fertile soil, herds, forest, mountain, volcano, sacred site, ores and fuels, park, wetland, dam, fish (sea), seed vault, great library, new people, and space resources (placed in the solar system view).
- **Events**: Nature, People and nature, People and power, Mystery, Modern world, Space, Futures. Each has an info popover.
- **Workshop**: custom elements and events. **Rules**: "When X, trigger Y" (including futures and energy conditions, and "end a future").
- **Random history** toggle, day/night, speed, full screen, save/load and world codes.
- **Right click** any object when zoomed in for its info; **i** on city labels for a people's details.
- On the globe and orbit views, **right click** an object in orbit (satellite, space telescope, space station, ring habitat, space cylinder, space elevator station or climber) for what it is and who built it.
- In the solar-system view, **left click** the Sun, the Moon or a planet for a close-up. The Sun shows the swarm in its builders' colours and who owns what share. The Moon and Mars show their named bases with their peoples and populations, colonies (with unrest or a war of independence) and Helium-3 rigs. Jupiter shows its ice moons and who mines them; the other worlds say who, if anyone, has been there. A click anywhere, scrolling or Esc zooms back out, and clicking Earth zooms back down to the globe. With a tool selected, a click still uses the tool. The close-up's text sits in a solid card on the right (below on narrow screens), and the body is sized so its rings, swarm or moons stay clear of it.
- Further out, **left or right click** a mining claim in the solar-system view (Helium-3 on the Moon, an asteroid mine in the belt, an ice moon at Jupiter) to see what it is, where it is and who mines it. In the galaxy view, click a generation ship (where it is bound, how far it has come, its crew) or a star colony (who founded it, when, how many live there). A tip stays open while its object exists and you stay on that view.
- **The galaxy** is the Milky Way seen from above its north pole: a golden central bar (~30,000 light years long), two major arms (Perseus, Scutum–Centaurus) starting at the bar's ends, two minor arms (Sagittarius, Norma/Outer) on 12° log spirals, blue-white arm stars with pink star-forming clouds, dust lanes and a faint disc. The Sun sits where it really is: about 26,000 ly from the centre, on the small Orion Spur between the Sagittarius and Perseus arms, with the bar's near end about 27° from the line to the Sun. Zoomed all the way out the view centres on the galaxy, with the Sun below the centre at first. No name labels are drawn there; click the Sun, the centre, a ship or a star colony to see what it is. The solar system (planets, swarm, claims, the Moon) fades out as the galaxy comes in, and colonies or ships so close to the Sun that they would sit on its marker are left out, so nothing piles up on the Sun.
  - **Free movement:** out at galaxy scale you can drag the view anywhere (mouse, touch), scroll sideways with a trackpad or use the arrow keys / WASD. The pan has limits so the galaxy cannot be lost, and Reset clears it. Zooming out from the solar system always brings the galaxy in centred; zooming in from wherever you roamed glides the view back to the solar system as part of the scroll (each notch brings it closer; it is home by the time the galaxy fades, about a dozen notches; it never moves on its own and zooming out does not undo it), then keeps zooming in from there (on the globe a drag turns the planet as before).
  - **It turns** (clockwise, arms trailing) with real disc-galaxy physics, sped up so one galactic year (230 million years) takes 10 minutes; it stands still while paused. Stars follow a flat rotation curve (`v = v0·r/√(r²+rc²)`): the core turns like a wheel (~90 s a turn), the Sun's orbit takes 10 min, the rim ~19 min, so the old disc shears. The bar is a rigid pattern at 1.45× the Sun's angular speed (~40 vs ~28 km/s/kpc); the arms are a density wave at 0.95× (the Sun just outside corotation), so the Sun slowly drifts relative to the arms and the arms slide along the bar's ends, meeting them again every ~20 min. Young blue stars and pink nebulae are born on the arms, drift out at their own orbital speed for their short lives (10–75 s on screen ≈ 4–30 Myr) and fade, which is why the arms never wind up. The Sun goes round the centre, so its place below the centre changes over time.
- In full screen the chronicle feed has a **Chronicle** toggle to fold it away. The choice is remembered, and while folded it shows how many new lines have come in.

## Futures (fates)

After the first people completes the Future Age, 13 futures build pressure from the state of the world (`FATES[*].drive`) with per-world random leanings (`bias`). Up to two start on their own (any number by hand from the Futures events). Each runs for a span, shown in the **Futures panel** with a countdown, then fades or, if its causes are still strong, **ends the world**.

| Future | Grows with | Content status |
|---|---|---|
| The Three-Sun Signal | answering the alien signal, Curious peoples, Stellar Age | **Full** (TB-01…08) |
| The Unravelling | pollution, climate, war, nuclear war, unrest | ending + new cycles and ruins (END-01/02); crises below feed it |
| The Waking Machines | machine autonomy (top people and world average), AI events, Curious peoples | machine autonomy meter (AGI-01), reactions by character (AGI-02), caretaker ending (AGI-03), war against the machines and The Iron Dominion (AGI-04), the merge (AGI-05), the grey spread and The Grey Tide (AGI-06): **full** |
| The Dying Sun | time after reaching space; certain by 40,000 CE | WE-01: the Sun swells to 3.2× its width and reddens over the countdown (sky turns amber, up to +2.6 °C: seas, snow, harvests; four chronicle lines; the Futures panel shows its width); if the future fades it settles back. WE-02: every human people from the Future Age on builds a planet engine (150 sim s at peace); any war slows everyone to 8% and a people at war builds nothing, so builders warm to each other and their wars end in treaties sooner; towers with blue jets on the strip, blue jets from the globe; the Long Voyage ending needs every engine finished (else the future fades at twice its span). WE-03: with every engine ready the world makes the journey (320 sim s): it leaves its orbit and the Sun falls behind, the day dims, the surface and seas freeze (to −36 °C), peoples move into lit cities under the ice (harvests safe), Jupiter swells to fill the sky and its pull brings a crisis (lives lost, far worse with war), then the deep voyage and the Long Voyage ending. Other futures fade when it begins (a Hevari fleet finds an empty orbit) and only a doom can end the world before it does. WE-04: at the end the world arrives or is lost (loss ~1 in 5 at peace with a clear Jupiter pass, 3 in 5 if scarred, more with war, less with many engines). Arriving, a new star (Barnard's Star, Tau Ceti, Epsilon Eridani, Luyten's Star or Wolf 359, each with its own light) comes near over 90 sim s: the dark lifts, the ice thaws, peoples climb out, then **A New Sun** (goal). Lost, the engines fail and the world drifts dark and frozen: **Lost in the Dark** (end). |
| The Great Upload | calm, prosperity, Curious/Mercantile | ASC-01: Future Age peoples upload their minds (about 170 sim s at full speed; Merged ×1.5, Curious ×1.3, Mercantile ×1, Warlike ×0.6, Devout refuse; paused during their own war); the land feeds only the bodies left so the living population falls, the minds are counted in the machines; buildings go dark one by one in a fixed order and lose their night lights; a cyan data centre grows beside the capital (right-click); card and Futures panel show the share uploaded. ASC-02: uploaded land rewilds fast (regrowth up to ×4, almost no footprint), forests and animals close in on the empty towns, and the dark buildings grow over one by one with vines, moss and young trees (about 140 sim s at full upload, and it goes on after the future ends); the chronicle tells of saplings in the streets, then of cities sinking under forest. ASC-03: when a people passes 60% uploaded, those who refuse break away on one edge of its land as a people of their own (Hearthfolk, Earthbound, Breathers…; Devout, or Warlike if their people were); Devout peoples who refused are holdouts too. Tension with the uploaded grows over about 120 sim s (faster for the Warlike and across a border): first insults, then sabotage of a data centre. It ends in war (likelier with Warlike holdouts, rarer with Mercantile neighbours or trade) or an uneasy peace. In war (a war of belief, slow to end in a treaty or bought off) the uploaded fly drones (strength ×1.2 at full upload) and the holdouts fight with zeal (×1.15); holdouts who win pull the plugs on the data centres (40% of the minds lost, all of them if they conquer), and if the uploaded win, the holdouts make peace on the machines' terms. |
| The Garden | peoples protecting healthy land, low pollution | GDN-01 the Garden path: a people with healthy land (forest over 50%, wild animals over 45%) under a Protect policy, in order and at peace, may choose to stay small: while the Garden future runs from the Industrial Age at 4% a second, otherwise only from the Information Age at 0.1% a second, by character (Devout ×1.5, Curious ×1, Merged ×0.8, Mercantile ×0.5, Warlike never). Over about 120 sim s the land feeds fewer (carrying capacity × 1 − 0.6 × share), so the population shrinks gently; towns drop size tiers and towers come down to tree height; roofs, terraces and fields turn to gardens; forests close in and regrow faster (×2.5) with a light footprint; stability drifts up; the policy stays Protect. A war forced on them, or failing land, ends the choice and the cities grow back. GDN-02 the Garden ending: when every living people (two or more) is at least 80% along the path, no war is being fought, and the world's forests stand at 70% or more and its wild animals at 60% or more, the world holds its breath; held for 30 sim s (any people leaving, a war or failing nature breaks it), history ends in the Garden World (a goal). While the Garden future runs, the example of the neighbours draws every people, even the Warlike, by half the share already on the path, so a world nearly all gardeners can finish the job; and while it runs any people with fair land (forest and wild animals over 35%) may join, whatever its policy (joining sets Protect). It stays rare: in sampled natural worlds the Garden future ran in about 1 in 4, and in one every people joined at once before another ending came first. The Garden future no longer ends with it on its drive alone: without a Garden world it fades. The epilogue lists the gardeners, forests, wild animals, the people against the height of the cities and the years at peace, with a closing story. |
| The Great Silence | peoples in space | placeholder (SIL) |
| The Watcher | player interventions | placeholder (SIM) |
| The Branching | Stellar/Galactic peoples | placeholder (SPE) |
| The Long Night | unrest, war, pollution | placeholder (NGT) |
| Dimming the Sun | warming | placeholder (GEO) |
| The Invitation | long peace in space | placeholder (FC) |
| The Ageless | well-fed, stable, Mercantile | placeholder (IMM) |

### Endings (19)
- **The world falls** (survivors lose most people; "Begin again from the ruins" starts a new cycle, and if you keep watching the survivors begin again on their own after 40 sim seconds): The Fall, The Flattening, The Long Night, Snowball Earth, **The Long Winter** (nuclear winter), **The Empty Cities** (engineered plague), **The Ash Years** (supervolcano), **The Great Impact** (asteroid).
- **History changes for good**: The Quiet Takeover, The Ascension, The Silence Kept, Beyond the Glass, Many Humanities, The Ageless Empire, The Reservation.
- **Humanity arrives**: The Garden World, Among the Stars, The Long Voyage, The Edge of the Galaxy (completing the Galactic Age).

Each has a colour wash on the map and an epilogue card (furthest age, peoples, wars, futures, survivors, escaped ships).

### The Three-Sun Signal (inspired by Liu Cixin's The Three-Body Problem; original names)
Reply from the Hevari of Hevar → fleet countdown → sentinels lock physics (no new ages) → stances by character (Defenders, Escapists, Worshippers, Defeatists) → hidden strategist (player can choose; deterrent / bluff / escape ark) → the probe destroys the fleet → deterrence (holder tested every ~50 s; may hold, fail, or broadcast) → broadcast → dark forest strike (the world flattens like a painting) **or** fleet arrives → occupation and resistance → resistance wins or The Reservation. Event: Broadcast the Coordinates.

## The end of the world (END epic)

- **New cycles (END-01).** A world that falls is never dead while anyone survives: the survivors restart in the Prehistoric or Stone Age (Stone Age if they had reached the Industrial Age), the clock keeps running, nobody keeps the bomb, and the age line under the year shows the cycle ("The Stone Age · Second rise"). If no one survives, the world stays dead and only "New world" is offered.
- **Ruins (END-02).** When a world falls, and when a people of the Bronze Age or later is conquered or dies out, its tallest buildings become ruins: rusted towers, broken domes, fallen walls and, from the Industrial Age, a buried highway. Nature covers them over ~700 sim seconds (vines, mounds, sinking slabs). They show on the strip (right click for who left them, how overgrown, who scavenges) and as rust-grey specks on the globe. A people at least two ages behind the ruins on its land learns up to 45% faster, less as the ruins grow over.
- **Nuclear winter (END-03).** A nuclear war with two or more nuclear powers is a full exchange: soot darkens the sky for 70 sim seconds (harvests fail, a "Nuclear winter" effect on every people). Modern peoples dig **bunkers** (Devout peoples: **deep vaults**) while the doomsday clock is at 7 minutes or less, faster for Warlike peoples and when it is at 4 or less; bunkers dug after the bombs fall do not count. Bunkers soften the strike and the winter. When the winter ends, if fewer than half the living peoples are sheltered, unsheltered peoples may die out and the world falls (**The Long Winter**). A one-sided strike only darkens the sky for a while.
- **Runaway warming (END-04).** Heat above +1.6 °C adds up (degree-seconds); at 4 the warming feeds itself: temperature keeps climbing (to about +5 °C) while there is pollution, the seas rise up to ~70 m and visibly drown the coasts on the strip, the minimap and the globe, coastal peoples lose food and stability, refugees pour into neighbours and relations sour into wars over land. Dimming the Sun or the Garden stops it at once; otherwise it fades only once the air is clean and the temperature falls below +1.2 °C. The seas then recede slowly. Climate Change now also happens on its own in the Industrial to Future Ages, more often when pollution is high.
- **Engineered plague (END-05).** An event (Modern world, from the Future Age) and a rare random event once per cycle. It spreads along contact between peoples (faster during trade booms and between friends), kills far more than natural plague and stops births while it lasts. Peoples may close their borders when it starts (Devout most often, Mercantile least; the "closes borders" reaction does it too), which slows it greatly. If humanity falls below 30% of its size at the outbreak, the world falls (**The Empty Cities**).
- **Supervolcano and killer asteroid (END-06).** *Supervolcano* (Nature event; very rarely on its own at a Volcano, once per cycle): buries the peoples near it (up to ~55% dead, far peoples ~8%), leaves a caldera, and starts a 60 s volcanic winter. *Killer Asteroid* (Space event; very rarely on its own once a people reaches the Modern Age, once per cycle): a named rock with a 140 sim-second countdown, seen at once from the Modern Age, otherwise only as a brightening star in the last 25 s; it shows in the sky growing brighter. Every 26 s the best-placed people from the Future Age launches a deflection mission: earlier tries, more advanced and Curious peoples and space bases do better; a failed try can chip it smaller. In tests Future Age peoples saved the world about half the time, Stellar Age peoples about three times in four. An impact kills 25–70% (more where it lands), leaves a huge crater and an impact winter. After either winter, if humanity is below 30% of its size, the world falls (The Ash Years / The Great Impact); a rock of the largest size always ends it.
- **Seed vaults and libraries (END-07).** Two elements under "Keeping the past". When the world falls, each surviving people's start depends on what its land holds (judged by the age it had reached at the fall): nothing → Stone Age if it had reached the Industrial Age, else Prehistoric; **Seed Vault** → at least the Stone Age, twice the people, food 78; **Great Library** (from the Bronze Age) → a third of the age it had reached, plus one, at most the Iron Age, with 40% progress; both → one age further. Peoples also build them: libraries from the Classical Age when culture is high, seed vaults from the Information Age, much more often when danger looms (a winter, warming, plague, asteroid, collapse fate or a near-midnight clock); at most two of each are built this way per world. The chronicle and the epilogue ("Kept safe") say who kept what.
- The world line under the year shows "nuclear winter", "volcanic winter", "impact winter", "asteroid: impact in N years", "runaway warming", "seas +N m" and "engineered plague"; people cards show Bunkers / Deep vaults, Plague N%, Borders closed, Coasts drowned N%, Scavenging ruins.

## Space

Orbit layer (satellites, telescopes, stations, ring habitats, space elevators, cylinders, debris and cascades) · Moon and Mars bases with life-support failures · helium-3, asteroid mines, ice moons held by the best-placed people · energy scale Type 0–3 with milestones · Dyson swarm that dims the Sun · colonies becoming peoples, independence wars · generation ships to real nearby stars with voyage events; large, old star colonies send ships of their own to the nearest free star, so settlement spreads from colony to colony · galaxy view · space events (solar flare, colony strike, life-support failure, debris cascade, rogue comet).

## Nature

A 120-cell grid of forest, wildlife, soil and fish; peoples clear, hunt, farm and fish by age and policy; extinctions (mammoth, aurochs, whales…); parks and rewilding; floods worse without forest and wetland.

## Machine autonomy (AGI-01)

Each people has a **Machines** meter (0–100): how much of its decisions it has handed to thinking machines. It shows on the people card from the Information Age.

- It rises from the Information Age, faster with progress through the age, faster again in the Future Age and beyond.
- Character: Curious ×1.7, Mercantile ×1.15, Warlike ×1, Devout ×0.35. The rise slows near what each character will accept (Curious 100, Mercantile 88, Warlike 78, Devout 45).
- An AI Awakening adds +20 at once and triples the rise while it lasts.
- Chronicle lines at 30, 60 and 90; a "Machines in charge" chip from 75. Above 50 the machines speed progress a little.
- It feeds The Waking Machines: the most automated people (from 25) and the world average (from 15). A new cycle starts at 0.
- Real data (24 natural worlds, 3,000 s): every world passes 30 (Future or Planetary Age, almost always a Curious people first); 90 is rare. The Waking Machines began in 17 worlds (16 before) and ended 6.

## Answers to AI pressure (AGI-02)

A new reaction stress, `ai`, comes when a people's meter passes 30/60/90, every 50–90 s while it is 15+ (Information Age on), after an AI Awakening, and for every people when The Waking Machines begins. Each character answers mostly (~90%) in its own way:

| Character | Answer | Effect |
|---|---|---|
| Curious | race ahead | progress +14, stability −4, meter +8 |
| Devout | ban the machines | meter −15, rise ×0.15 and progress ×0.85 for 90 s ("Machines banned"), culture and stability +8 |
| Warlike | machine army | military +25, meter +5, "Machine army" for 60 s, relations −4 with every people in contact, who feel threatened |
| Mercantile | sell the machines | meter +6 for every people in contact from the Information Age on, relations +8, food +6, progress +5 |

A people's own choices push the meter only up to its character's ceiling (`machNudge`); an AI Awakening can go past it.
Real data (24 worlds): Curious end near 100, Mercantile ~70, Warlike ~65–70, Devout ~10. Waking Machines outcomes about the same as AGI-01 (began in 20 worlds; 4–8 endings across runs). War counts stayed within the noise between runs.

## The caretaker ending (AGI-03)

When The Waking Machines ends the world ("The Quiet Takeover", kind *end*), the machines quietly take charge (`W.care`):

- **Who:** every living people, except those whose meter is under 30 (the people with the most machines is always taken). Holdouts "refuse the care of the machines and keep their own counsel"; a holdout whose own meter later reaches 60 gives in and joins.
- **Peoples in care:** no wars (none can start, join or be ordered, and a nuclear order is refused), no reactions (humans no longer decide), no progress (tech never rises, so no new age), stability pulled to ~90, food to ~85, military to ~10, meter fixed at 100. Their land regrows 2.5× faster and is cleared 5× less; each adds −0.4 to pollution.
- **The world:** other futures fade and no new ones begin. A caretaker line enters the chronicle every 45–75 s (harvests, disbanded armies, returning forests, "Nothing new has been invented in …").
- **Holdouts** go on as before: they progress, and can fight each other but not the peoples in care.
- **Epilogue:** its own rows (who is in the machines' care, who is outside, the year of the last human decision) and a closing line that depends on whether anyone is still outside. The people card shows "In the machines' care" (with "No new age will come") or "Outside the machines' care". Violet caretaker drones hover over the cities in care.

Real data (24 natural worlds, 3,000 s, then 400 s under the caretakers): 4 worlds ended in the takeover, each with one Devout holdout (meter 5–14). Devout peoples top out at 45, so they never give in on their own. There were 0 wars involving peoples in care and 0 progress for them. Stability rose from 41–58 to 85–89, and the forest share in their lands from 0.35–0.63 to 0.94–0.98.

## War against the machines (AGI-04)

During The Waking Machines, each people with a meter of 70+ may see its machines rise. The chance is 0.25% per second, ×2.5 for Warlike, ×0.8 Curious, ×0.5 Devout, ×2 with a machine army and ×2 when stability is under 35. There is at most one uprising per cycle and room is needed (fewer than 8 peoples). The player can also click **Machine Uprising** (Modern events, Information Age on); it starts The Waking Machines if needed.

- **The machine people** (`c.machine`, grey `#9aa3ad`, named Automata, Iron Host…) takes the far side of its makers' land. It starts with 40% of their population. The makers keep 70% of theirs, lose 30 stability and their meter drops to 15.
- **How it lives:** no births (it builds units in factories, faster on wider land), food fixed at 100, stability ~88, military ~92, no progress, no reactions, never makes peace (no treaties, humans cannot appease it). It is 1.5× stronger than a people of the same size and age, doesn't catch plagues, and clears and pollutes its land.
- **Its looks:** a red-eyed machine core, drone factories with sawtooth roofs and blinking lights, exhaust stacks and relay pylons. No farms, houses, roads, trains or planes; hovering drones and walking robots instead of people.
- **The humans** end every war among themselves at once ("Old enemies make peace overnight"), relations among them rise, other humans join the war, and their meters drop by 40%. The whole machine war counts as one war for the futures (Collapse and the others).
- **Outcome**, judged on the machines' share of their own continent (they cannot settle across the sea):
  - The machines win (**The Iron Dominion**, kind *end*) if they hold 80%, overrun 2 peoples, or still hold 55% after 320 s.
  - The humans win if the machines are destroyed, or by cutting their power at 320 s if the machines hold less than 55%. Thinking machines are then banned for 300 s and every meter drops to 10 or less.
  - The Waking Machines cannot end by its countdown while the war goes on. If the world falls in a doom ending meanwhile, the machines rust and the new cycle has none.
- **UI:** the futures panel reads "War against the machines · they hold N% of their continent". The card shows "Machine mind · No births" and a "Machine people" chip. The Iron Dominion epilogue lists the machines, their share, peoples overrun and the humans left.

Real data (36 natural worlds, 3,000 s):
- 16 uprisings in 16 worlds (Curious 9, Warlike 7).
- The machines won 3 and the humans won 9. 1 world fell during the war, and 3 runs ended before the war did.
- Largest machine share: 0.33–1.0.
- Endings: Iron Dominion 3, caretakers 4.

The first versions never let the machines win. Share was counted across all four continents, so it never passed 0.18. Warlike peoples could never rise: their meter is capped at 78, below the first threshold of 80. Each human that joined the war counted as a separate war, which pushed Collapse to end the world in 6 of 12 wars.

## The merge (AGI-05)

During The Waking Machines, a people in the Future Age or later whose meter is 85+ (and with no ban in force) can answer AI pressure by merging with its machines (`mergeai`). The weights are Curious 3, Mercantile 2, Warlike 1 and Devout 0; Warlike peoples cap at 78, so they only get there after an AI Awakening. The player can also click **Merge with the Machines** (Modern events, Future Age on).

- **Character:** it becomes **Merged**, a fifth character that no people is born with (`BASE_TRAITS` holds the four birth characters). Its old one is kept (`c.oldTrait`). Merged means progress ×1.4, half the births, stability +8, culture +12 and military +8. It answers stress calmly: innovate, trade, reform, conserve, ally, appease. It faces no more AI pressure, and its machines can never rise (no uprising, and the event refuses). It keeps its land policy.
- **Looks:** people in pale suits with glowing cyan implants. Neural towers (glowing spines and nodes) and neural hubs (lattice domes) appear among the age's own buildings. The hub is the centrepiece and there are no fields. At night the towers are linked by arcs of light with pulses running along them.
- **UI:** a "Merged (once Curious)" chip, "Neural Commonwealth · One mind with its machines" on the card, and "Merged" in the character menu (switching to another character unmerges). The epilogue lists the merged peoples.
- **A new cycle:** merged peoples wake up alone and get their old character back.

Real data (36 natural worlds, 3,000 s, final tuning): 21 merges in 18 worlds (19 Curious, 2 Mercantile), all during The Waking Machines, in the Future to Galactic Ages. Uprisings: 11 (the machines won 1, the humans 7). Other futures and wars stayed within the noise.

The first version allowed merging at any time and set the 'protect' land policy. That gave 45 merges in 31 of 36 worlds, and Garden futures tripled (8 to 24, with 9 Garden endings). Merging was then limited to The Waking Machines, peoples keep their policy, and the Curious weight went from 5 to 3. Taking Curious peoples out of the uprisings lowers how often the machines win (3 of 12 before AGI-05, 0–1 after); this is a point for the FND-08 balance pass.

## The grey spread (AGI-06)

During The Waking Machines, a people in the Future Age or later whose meter is 80+ can lose control of self-copying machines (rate per second `GREY_RATE` × Curious 1.5, Mercantile 1.2, Warlike .8, Devout .3; once per cycle; not while machines are at war or under the caretakers; never together with an uprising). The **Grey Spread** event starts it where the player clicks.

- **Spread:** one value per 100-pace nature cell (`W.grey.g`). Each cell grows on its own and creeps into its land neighbours; machines from a more advanced people copy faster (`k` = 1 + .3 per age past the Future Age). It never lives on the sea, but now and then a thick coastal cell seeds a new stain on another continent ("Grey machines wash ashore…").
- **What it does:** forests turn to silicon (forest → 0), animals vanish, the soil dies, and nothing grows back under it. Peoples on grey land lose food, people and stability.
- **Fighting it:** every people with grey in or near its lands burns it back with a budget per second: age, army, character (Warlike 1.4, Curious 1.2 with counter-swarms, Mercantile 1, Devout .8, Merged 1.5) and low stability. Full strength comes 60 s after it first meets the grey, and its reach grows as the fight goes on (space peoples reach further). A patch caught early burns out; a wide front overwhelms them. Fighting costs stability and adds some pollution. Each people gets a chronicle line in its own voice. **Burn the Grey** lets the player burn it away where they click.
- **Flight to space:** a Planetary Age or later people whose land is half grey sends ark ships to the stars (counted as escaped in the epilogue; most of its people leave).
- **Outcomes:** *stopped* (the last of it burned away; those who fought trust their machines less), *stalled* (after 480 s copying errors stop it where it is), or **The Grey Tide** (a doom ending) when it covers half the land. A stalled or ended grey stays as a dead crust that weathers away over the next cycle. While it is live, no other future ends or fades and the Galactic edge waits.
- **Looks:** a steel-grey crust over the ground, silicon spires where the trees stood (right click: "Silicon spire" / "Dead grey crust"), a glittering front where it is thin; a grey stain on the strip map and on the globe. Futures panel: "Grey spread · N% of the land"; top bar: "grey spread: N% of the land"; card chips "Grey N% of the land" and "Fled to space".

Real data (108 natural worlds, 3,000 s, twice): 32 greys in 27 worlds and 15 in 15 worlds (from Curious and Mercantile peoples, Planetary to Galactic Age). Outcomes: stopped 16 + 11, ended the world 8 + 2, stalled 3 + 2 (others were cut short by an unrelated ending or the end of the run). Collapse endings and other counters matched the old build within run-to-run noise (collapse per world 0.44 old vs 0.24 and 0.43 new).

The first version was far too weak: every patch burned out in 3 s, because peoples answered at full strength at once. Then, with a mobilisation ramp, natural worlds had only 1 grey in 36, burned out in 12 s, since by the time the meter reaches 80 peoples are Stellar or Galactic. Machines that copy faster when their makers are advanced, a higher rate, a half-the-land ending and holding other futures while the grey is live gave the mix above.
