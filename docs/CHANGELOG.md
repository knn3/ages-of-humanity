# Changelog

What was built, in order, from the user's requests (newest last). Published artifact versions are listed in the artifact's history.

## Early development (before the tracker)
1. **The game**: a 2D side-scrolling simulation of civilisation from the Stone Age to the information age and beyond, where the player adds elements and events and peoples react. (Interstellar part deferred.)
2. **12 ages** (Prehistoric → Future), a bigger world with ocean between landmasses.
3. **Scroll to zoom** and **full screen** mode.
4. **Free drag** in all directions.
5. **Globe zoom**: zooming far out bends the world into a globe through the Troposphere, Stratosphere, Mesosphere, Thermosphere and Exosphere into space.
6. **Nature**: forests, wildlife, soil and fish, and what peoples do to them (clearing, hunting, parks, rewilding, extinctions).
7. **Info redesign**: names only, with an **i** for details.
8. Hover only when zoomed in; underground deposits get info; **normal cursor**.

## Futures plan
9. Brainstorm of future scenarios (Three-Body, intergalactic, end of the world, AGI, plus more); **64 tickets in 15 epics** created in the tracker.

## Foundation (FND)
10. **FND-01** fate engine: pressures from world state, up to two futures at once.
11. **FND-02** three space ages (Planetary, Stellar, Galactic) with buildings, clothing, governments, reaction texts.
12. **FND-03** Futures panel with countdowns, "Gathering" list, ribbon markers.
13. **FND-04** Futures events (start any future by hand).
14. **FND-05** endings, epilogue card, "Begin again from the ruins" cycles.
15. **FND-06** saves checked for every new structure; countdown fix (always counts down).
16. **FND-07** rules for futures (begins, years left, ends, world ending; end a future).
17. **FND-08** first balance pass (slower space ages, easier endings, more varied futures). *Still in progress.*

## Map info changes requested along the way
18. Info only when zoomed in very close and only on objects; city info moved to an **i** on the city label; tighter hit areas.
19. Info opens on **click**, then on **right click** (final), for buildings, people, vehicles, animals, trees, ships, soldiers, craters, borders, elements and deposits.
20. Map type reassessed (side view + overview suggested); **the user chose to keep the map as it is.**

## Into space (SPC)
21. **SPC-01** orbit layer and debris cascades. **SPC-02** solar system view.
22. **SPC-03** Moon and Mars bases. **SPC-04** space resources (helium-3, asteroid mines, ice moons) as keys. **SPC-05** energy scale (Kardashev). **SPC-06** Dyson swarm and space cylinders. **SPC-07** colonies become peoples, independence wars.
23. **SPC-08** generation ships. **SPC-09** galaxy view. **SPC-10** space events. Thorough test pass (17 scripts, 12 natural lifecycles, perf at every zoom, 260-action fuzz).

## Three-Body (TB), inspired by Liu Cixin
24. **TB-01…05**: the Hevari reply and fleet, physics lock, stances, hidden strategist, the probe.
25. **TB-06…08**: deterrence, broadcast and the dark forest strike (the flattening), fleet arrival, occupation, resistance, The Reservation ending.

## End of the world (END), 2026-11-22
27. "Run the next 5 jobs and run the test": **END-01** collapse begins again on its own (new cycle after 40 s, cycle counter, no bombs carried over, dead world if no survivors). **END-02** ruins (rusted towers, broken domes, fallen walls, buried highways) that grow over, show on the strip and the globe, and speed up younger peoples who scavenge them. **END-03** nuclear winter after a full exchange, bunkers and deep vaults, The Long Winter ending. **END-04** runaway warming past a tipping point, rising seas drowning the coasts, refugees and wars over land, stopped by Dimming the Sun or the Garden. **END-05** engineered plague spreading along contacts, closed borders, The Empty Cities ending. New tests `endworld.py` (29 checks) and `endnat.py` (natural runs).

## Packaging
26. This folder: game, CLAUDE.md, docs, tests and tickets (xlsx/csv), for other agents to continue.
