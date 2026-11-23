#!/usr/bin/env bash
# Runs the regression set in parallel (JOBS at a time, default 6) and prints a one-line result per script.
# Optional: export CHROME=/path/to/chrome (otherwise Playwright's own Chromium is used).
cd "$(dirname "$0")"
TESTS="endworld end06 end07 agi01 agi02 agi03 agi04 agi05 orbittip bodies fslog galaxy run2 saves rules futev futpanel epi fates ages orbit system spaceplace spaceev tbui clicktip3 picks labinfo hover4 hover5 perf_fuzz"
mkdir -p out
# at most JOBS scripts at once (default 6): starting every browser together times out page loads
export JOBS=${JOBS:-6}
printf "%s\n" $TESTS | xargs -P "$JOBS" -I{} sh -c 'python3 "{}.py" > "out/{}.txt" 2>&1; echo "exit $?" >> "out/{}.txt"'
for t in $TESTS; do echo "$t: $(tail -1 out/$t.txt) | PASS lines: $(grep -c PASS out/$t.txt) | page errors: $(grep -c 'PAGEERR\|Traceback' out/$t.txt)"; done
