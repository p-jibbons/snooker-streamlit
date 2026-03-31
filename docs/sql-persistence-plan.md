# SQL Persistence Plan

This document outlines a bounded SQL-backed persistence design for the snooker app.

## Goals

- Move beyond JSON-only storage toward a small embedded database.
- Keep the app simple to run locally with no separate server.
- Support current features first:
  - current frame state
  - running match state
  - completed frame history
- Leave room for upcoming backlog items:
  - simple user registration
  - player assignment to games
  - leaderboard/stat tables

## Recommended database

Use **SQLite** in the project-local `data/` folder.

Why:
- zero extra service to install
- built into Python via `sqlite3`
- good fit for a local Streamlit app
- easy to back up alongside the project
- sufficient for small-table, single-user or light local use

## Proposed file location

- database file: `data/snooker.db`

Keep current JSON saves during transition if helpful, then either:
- treat them as compatibility snapshots, or
- retire them after the SQL path is stable

## Design principles

1. **SQLite is the source of truth** for persisted app data once implemented.
2. Keep the schema normalized enough for stats queries, but not over-engineered.
3. Store detailed current-frame state in a compact serialized payload when that is simpler than over-modeling every transient field.
4. Store completed-frame and match summary data in relational tables for leaderboard/stat queries.
5. Use idempotent schema bootstrap on app startup.

## Main entities

### 1. players
Registered users for future player selection and leaderboard support.

Suggested columns:
- `id` INTEGER PRIMARY KEY
- `display_name` TEXT NOT NULL UNIQUE
- `created_at` TEXT NOT NULL
- `is_active` INTEGER NOT NULL DEFAULT 1

Notes:
- no auth required for the current POC
- names should be unique enough for simple local usage

### 2. matches
One multi-frame session between two selected players.

Suggested columns:
- `id` INTEGER PRIMARY KEY
- `player1_id` INTEGER NULL
- `player2_id` INTEGER NULL
- `player1_name_snapshot` TEXT NOT NULL
- `player2_name_snapshot` TEXT NOT NULL
- `best_of` INTEGER NOT NULL
- `frames_won_p1` INTEGER NOT NULL DEFAULT 0
- `frames_won_p2` INTEGER NOT NULL DEFAULT 0
- `status` TEXT NOT NULL DEFAULT 'in_progress'
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL
- `completed_at` TEXT NULL

Notes:
- keep both player ids and name snapshots
- snapshots preserve readable history even if a player name changes later

### 3. frames
Completed frame records for history and stats.

Suggested columns:
- `id` INTEGER PRIMARY KEY
- `match_id` INTEGER NOT NULL
- `frame_number` INTEGER NOT NULL
- `winner_player_slot` INTEGER NULL
- `winner_player_id` INTEGER NULL
- `winner_name_snapshot` TEXT NULL
- `player1_score` INTEGER NOT NULL
- `player2_score` INTEGER NOT NULL
- `ended_by` TEXT NOT NULL
- `created_at` TEXT NOT NULL

Suggested `ended_by` values:
- `clearance`
- `respotted_black_pot`
- `respotted_black_foul`
- `manual_reset`
- `other`

Notes:
- this table powers frame history and later leaderboard summaries
- `winner_player_slot` is likely 1 or 2 for simple querying

### 4. app_state
Small key/value table for resumable in-progress state.

Suggested columns:
- `key` TEXT PRIMARY KEY
- `value_json` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

Suggested keys:
- `current_frame`
- `current_match`

Notes:
- use this for transient in-progress state that maps closely to current JSON saves
- keeps the first SQL iteration small and low-risk

## Relationships

- one `match` has many `frames`
- a `player` can appear in many `matches`
- a `player` can win many `frames`
- `app_state` is standalone key/value storage

## Data flow

### App startup
1. Open SQLite connection.
2. Run schema bootstrap if tables do not exist.
3. Load `app_state.current_frame` into `SnookerGame`.
4. Load `app_state.current_match` into lightweight match state.
5. If no saved SQL state exists yet, optionally fall back to existing JSON files.

### During frame play
- scoring actions update in-memory game state
- after each successful action:
  - save current frame payload into `app_state.current_frame`
  - save current match payload into `app_state.current_match` if needed

### When a frame is completed and recorded
1. insert one row into `frames`
2. update `matches.frames_won_p1/frames_won_p2`
3. update `matches.updated_at`
4. if match winner reached target, mark `matches.status = 'completed'`
5. reset or replace `app_state.current_frame`

### When future registration is added
- create/select rows in `players`
- create new `matches` rows referencing selected players
- keep snapshot names in case display names change later

## Serialization approach

For the current frame and current match, store JSON payloads in `app_state`.

Examples:
- `current_frame` -> serialized `SnookerGame`
- `current_match` -> JSON with:
  - selected player ids if present
  - selected player names
  - frames won
  - best_of
  - active match id if persisted in `matches`

Why this hybrid approach:
- low migration risk from current JSON files
- avoids prematurely flattening every transient gameplay field into columns
- still enables structured historical queries through `matches` and `frames`

## Migration approach

### Phase 1 — bootstrap SQL alongside existing JSON
- add SQLite connection helper
- add schema creation
- mirror current JSON persistence into SQL app-state records
- keep tests focused on bootstrap and round-trip persistence

### Phase 2 — use SQL as primary storage
- load from SQL first
- optionally import from JSON if SQL is empty
- continue writing current state to SQL on every action

### Phase 3 — persist historical records relationally
- create/update `matches`
- insert `frames` rows when a frame is recorded
- derive frame history UI from SQL instead of only in-memory/session state

### Phase 4 — build player and leaderboard features
- add `players`
- assign players to matches
- query stats from `matches` and `frames`

## Validation and testing plan

Minimum tests for implementation:
- schema bootstrap creates expected tables
- loading empty database returns default app state
- saving/loading current frame round-trips cleanly
- saving/loading current match round-trips cleanly
- recording a completed frame inserts frame history and updates match totals
- repeated bootstrap is safe and idempotent

## Open questions

- whether to keep JSON saves as export/debug artifacts after SQL stabilizes
- whether each new match should get a persisted `matches` row immediately or only after player registration lands
- whether undo should remain memory-only or persist to SQL snapshots

## Recommendation for next implementation step

Implement **T2 + T3 in a narrow way**:
- add SQLite bootstrap and connection helper
- add `app_state` table first
- round-trip current frame and current match through SQLite
- keep historical `matches`/`frames` table creation in place even if initial writes are limited

That preserves momentum without trying to solve registration, leaderboard logic, and full migration all at once.
