# Workflow and collaboration notes

## How the user works
- Asks in short messages: "next job", "run the next 5 jobs and test with real data", "finish all SPC series and test everything thoroughly".
- Expects each job to be **implemented, tested, published, and its ticket set to Done**, then a short report: what was built, what testing showed (with numbers), bugs found and fixed, what's next.
- Gives UI feedback with screenshots; apply it directly and keep the preference afterwards (see CLAUDE.md "Hard rules").
- Said "no, keep everything as it is" to a map redesign proposal: don't re-propose it.

## Tickets
- Source of truth: the live tracker sheet (see CLAUDE.md Links); offline copy `tickets/tickets.xlsx`.
- Columns: ID, Title, Epic, Priority (P1–P3), Status (To do / In progress / Done), Size (S/M/L), Description, Done when, Depends on. The **Epics** sheet counts tickets and progress per epic with formulas.
- Order of work so far: by ticket ID within epics, epics in tracker order. P3 epics are smaller "future flavours".
- If you can't reach the live sheet, update `tickets/tickets.xlsx` (and tell the user the live sheet needs the same change).

## Definition of done for a ticket
1. Meets the ticket's "Done when".
2. Works in **natural worlds** (no forcing) as well as by hand.
3. New state survives save/load and old saves still load.
4. No page errors in the regression set; draw time not noticeably worse.
5. New systems reachable via `window.__aoh` for tests.

## Publishing
`mcp__claude-artifacts__publish_files` with slug `7b7f2273-f157-4b5c-be02-fa01dc003a2a`, `files: [{as: "index.html", path: <local path>}]`, `base_version` = current version (from `get_artifact` or the last publish), short `label` naming the ticket(s).
