# AGENTS.md

## Goal
This repo is a personal toolbox of small utilities. Keep it easy to scan and hard to forget what each script does.

## What Is In This Repo

| Path | Type | Purpose |
| --- | --- | --- |
| `updaten8n.sh` | shell script | Recreate the `n8n` Docker container on latest image with existing volume settings. |
| `updaters/updateAItools.sh` | shell script | Update/install common AI CLI tools globally (`codex`, `gemini-cli`, `opencode-ai`, `claude`). |
| `model-runners/nemotron-1m-24gb.sh` | shell script | Start `llama-server` with Nemotron GGUF and a 1M token context setup. |
| `mongo-scripts/mongo-backup.py` | Python script | Interactive/non-interactive MongoDB backup utility using `mongodump`. |
| `notes/scrape_twitter_repos.md` | note | Scratchpad note with an example scraping approach. |

## Working Rules For Agents
1. Keep root `README.md` as the source-of-truth inventory. Any added/renamed helper must be reflected there.
2. Prefer small, targeted scripts. Avoid framework-heavy rewrites unless requested.
3. Add a short header comment to new scripts explaining purpose and expected runtime dependencies.
4. Keep scripts idempotent when possible, and make risky behavior obvious.
5. Preserve user-specific defaults unless explicitly asked to generalize (ports, timezone, tool choices).
6. If behavior changes, document it in the README in the same change.

## Checklist For New Helpers
1. Put the helper in an existing category folder, or create a clearly named new folder.
2. Use a descriptive file name (`verb-target.sh`, `noun-task.py` style).
3. Make executable scripts executable (`chmod +x`).
4. Add/update usage docs in root `README.md`:
   - One inventory row
   - One short usage example
   - Prerequisites if needed
5. Run a basic sanity check (`bash -n`, `python -m py_compile`, or direct dry run where possible).

## Out Of Scope
- Do not store secrets in scripts or notes.
- Do not add long-form docs unless they are directly useful for running a helper.
