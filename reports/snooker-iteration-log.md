## 2026-03-30 11:41 PDT
- current task: Add a bounded first-pass match-tracking layer on top of the existing frame tracker.
- what changed: Added persisted match-state storage (match_state.json), surfaced best-of and frames-won controls in the Streamlit sidebar, added match summary/status UI, and documented the new capability in the README.
- blocker or uncertainty: This is intentionally lightweight match tracking only; it does not yet keep a full frame-by-frame match history or per-frame archive.
- decision taken: Chose the smallest safe step toward multi-frame support without refactoring the existing frame engine.
- verification result: ./.venv/Scripts/python.exe -m pytest -> 21 passed.
- next step: Add proper per-frame archival/history so completed frames can be reviewed instead of only incrementing the running match score.

## 2026-03-30 12:12 PDT
- current task: Add a minimal completed-frame archive on top of the new match tracker.
- what changed: Extended persisted match state with frame_history, recorded winner/final score whenever a frame is banked into the match score, surfaced recent completed frames in the UI, and updated storage tests and README coverage for the archive.
- blocker or uncertainty: Existing repo changes were already present, so this iteration stayed narrowly scoped and did not attempt deeper match-history refactors like per-frame timestamps or full frame-state snapshots.
- decision taken: Implemented the smallest safe reviewable history layer that builds directly on the current frames_won flow.
- verification result: ./.venv/Scripts/python.exe -m pytest -> 21 passed.
- next step: Consider richer multi-frame history details (for example timestamps or per-frame metadata) only if they can be added without disturbing the current stable frame engine.

## 2026-03-30 21:22 PDT
- current task: Fix leaderboard played-count logic so recorded matches credit both participants, not just the winner.
- what changed: Reworked leaderboard aggregation to join completed frames back to their match player snapshots, count appearances for both registered participants, keep win totals aligned to registered names, and tightened the storage test to seed real match rows and assert correct played totals for winners and losers.
- blocker or uncertainty: The heartbeat backlog file referenced by HEARTBEAT.md was missing from the project, so task selection had to fall back to a clearly bounded bug visible in the current working tree.
- decision taken: Chose a contained correctness fix inside the already-active SQL/player feature branch rather than introducing a larger new feature on top of multiple uncommitted changes.
- verification result: ./.venv/Scripts/python.exe -m pytest -> 35 passed.
- next step: Restore or recreate reports/snooker-task-backlog.md so future heartbeat runs can choose ready tasks from the intended source of truth.
