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

- **Elements** (left click on land): river, fertile soil, herds, forest, mountain, volcano, sacred site, ores and fuels, park, wetland, dam, fish (sea), new people, and space resources (placed in the solar system view).
- **Events**: Nature, People and nature, People and power, Mystery, Modern world, Space, Futures. Each has an info popover.
- **Workshop**: custom elements and events. **Rules**: "When X, trigger Y" (including futures and energy conditions, and "end a future").
- **Random history** toggle, day/night, speed, full screen, save/load and world codes.
- **Right click** any object when zoomed in for its info; **i** on city labels for a people's details.

## Futures (fates)

After the first people completes the Future Age, 13 futures build pressure from the state of the world (`FATES[*].drive`) with per-world random leanings (`bias`). Up to two start on their own (any number by hand from the Futures events). Each runs for a span, shown in the **Futures panel** with a countdown, then fades or, if its causes are still strong, **ends the world**.

| Future | Grows with | Content status |
|---|---|---|
| The Three-Sun Signal | answering the alien signal, Curious peoples, Stellar Age | **Full** (TB-01…08) |
| The Unravelling | pollution, climate, war, nuclear war, unrest | ending + new cycles and ruins (END-01/02); crises below feed it |
| The Waking Machines | AI events, Curious peoples | placeholder (AGI epic) |
| The Dying Sun | time after reaching space | placeholder (WE epic) |
| The Great Upload | calm, prosperity, Curious/Mercantile | placeholder (ASC) |
| The Garden | peoples protecting healthy land, low pollution | placeholder (GDN) |
| The Great Silence | peoples in space | placeholder (SIL) |
| The Watcher | player interventions | placeholder (SIM) |
| The Branching | Stellar/Galactic peoples | placeholder (SPE) |
| The Long Night | unrest, war, pollution | placeholder (NGT) |
| Dimming the Sun | warming | placeholder (GEO) |
| The Invitation | long peace in space | placeholder (FC) |
| The Ageless | well-fed, stable, Mercantile | placeholder (IMM) |

### Endings (17)
- **The world falls** (survivors lose most people; "Begin again from the ruins" starts a new cycle, and if you keep watching the survivors begin again on their own after 40 sim seconds): The Fall, The Flattening, The Long Night, Snowball Earth, **The Long Winter** (nuclear winter), **The Empty Cities** (engineered plague).
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
- The world line under the year shows "nuclear winter", "runaway warming", "seas +N m" and "engineered plague"; people cards show Bunkers / Deep vaults, Plague N%, Borders closed, Coasts drowned N%, Scavenging ruins.

## Space

Orbit layer (satellites, telescopes, stations, ring habitats, space elevators, cylinders, debris and cascades) · Moon and Mars bases with life-support failures · helium-3, asteroid mines, ice moons held by the best-placed people · energy scale Type 0–3 with milestones · Dyson swarm that dims the Sun · colonies becoming peoples, independence wars · generation ships to real nearby stars with voyage events · galaxy view · space events (solar flare, colony strike, life-support failure, debris cascade, rogue comet).

## Nature

A 120-cell grid of forest, wildlife, soil and fish; peoples clear, hunt, farm and fish by age and policy; extinctions (mammoth, aurochs, whales…); parks and rewilding; floods worse without forest and wetland.
