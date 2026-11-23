# Ages of Humanity

A 2D side-view simulation of human civilisation, from hunters around a fire 200,000 years ago to peoples spread across the galaxy. Add rivers, herds, ores and forests, unleash droughts, plagues, inventors and comets, and watch each people respond in its own way. After the Future Age, the futures arrive: an alien fleet, collapse, thinking machines, a garden world, and more, each with its own ending.

## Play

Open **`index.html`** in Chrome, Edge, Firefox or Safari. No install, no server. (Fonts load from Google; offline it still works with plainer text.) Your world saves automatically in that browser.

Live version: https://claude.ai/artifact/GFVdMcCoxYPrnCGJKF9ihw (owner's account).

## Controls

| Action | How |
|---|---|
| Pause / resume | Space |
| Zoom | Scroll wheel, or − / + (zoom out far: globe → solar system → galaxy) |
| Move | Drag |
| Full screen | F (T shows the tools in full screen, Esc leaves) |
| Place an element or event | Pick it in the toolbox, then left click the land |
| Info about anything on the map | **Right click** it (zoomed in close) |
| Info about things in orbit (satellites, telescopes, stations, ring habitats, space cylinders, space elevators) | **Right click** them on the globe and orbit views |
| Info about things further out: mining claims in the solar system (Helium-3, asteroid mines, ice moons), ships between the stars, star colonies | **Left or right click** them in the solar-system and galaxy views |
| See the Sun's place in the Milky Way | Zoom all the way out; click the Sun or the galaxy's centre for what they are |
| Fold away the chronicle feed in full screen | Click **Chronicle** above it (remembered; while folded it counts new lines) |
| A close look at the Sun, the Moon or a planet | In the solar-system view, **left click** it (bases, colonies, mines and the Sun's swarm, and what is going on). Click anywhere, scroll or press Esc to zoom back out; clicking Earth takes you back down to the globe |
| Info about a people | The **i** on its city label |
| Details of a tool, event or future | Its **i** button |
| Reset view | Home |

## Folders

- `index.html`: the game
- `CLAUDE.md`: guide for AI agents continuing the work
- `docs/`: architecture, gameplay, testing, changelog, workflow
- `tickets/`: the full ticket list (Excel and CSV)
- `tests/`: headless Playwright tests
