#!/usr/bin/env bash
# Runs the regression set in parallel and prints a one-line result per script.
# Optional: export CHROME=/path/to/chrome (otherwise Playwright's own Chromium is used).
cd "$(dirname "$0")"
TESTS="endworld end06 end07 run2 saves rules futev futpanel epi fates ages orbit system spaceplace spaceev tbui clicktip3 picks labinfo hover4 hover5 perf_fuzz"
mkdir -p out
for t in $TESTS; do (python3 "$t.py" > "out/$t.txt" 2>&1; echo "exit $?" >> "out/$t.txt") & sleep 1; done; wait
for t in $TESTS; do echo "$t: $(tail -1 out/$t.txt) | PASS lines: $(grep -c PASS out/$t.txt) | page errors: $(grep -c 'PAGEERR\|Traceback' out/$t.txt)"; done
