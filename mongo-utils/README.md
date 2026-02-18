# mongo-utils

Utilities for MongoDB management.

---

## sync.js — One-way database sync

Syncs databases from a source MongoDB instance to a target. Uses additive upserts — documents in the target that don't exist in the source are left in place and reported at the end.

The `admin`, `config`, and `local` system databases are always excluded.

### Setup

```bash
npm install
cp .env.example .env
```

Edit `.env` with your connection strings:

```env
SOURCE_URI=mongodb://localhost:27017
TARGET_URI=mongodb://user:password@your-vps-host:27017
```

### Usage

```bash
npm run sync
```

You'll be prompted to select which databases to sync from a list of available databases on the source. Use **space** to toggle, **enter** to confirm.

### Output

Progress is shown per collection during the run:

```
── myapp
   users                           +12 new   ~847 updated   =231 unchanged   ! 3 orphaned
   sessions                        +0 new    ~0 updated     =1204 unchanged
```

A full summary is printed at the end:

```
══ SYNC SUMMARY ══════════════════════════════════════════════
  myapp
    users: +12 new, ~847 updated, =231 unchanged,   ! 3 orphaned in target
    sessions: +0 new, ~0 updated, =1204 unchanged

──────────────────────────────────────────────────────────────
  TOTAL  +12 new   ~847 updated   =1204 unchanged   ! 3 orphaned

  NOTE: Orphaned documents exist in the target but not the source.
  This sync is additive — they were left in place. Review manually if needed.
```

| Symbol | Meaning |
|--------|---------|
| `+N` | Documents inserted (new in source, didn't exist in target) |
| `~N` | Documents replaced (existed in both, source was newer) |
| `=N` | Documents unchanged (identical in both) |
| `!N` | Orphaned (exist in target but not in source — not touched) |
