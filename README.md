# hitesh-utils

Personal utility repo for one-off scripts, small automation helpers, and notes.

The goal of this README is simple: if a helper exists here, it should be listed here so it does not get lost.

## Helper Inventory

| Path | What it does | Run command |
| --- | --- | --- |
| `updaten8n.sh` | Pull latest `n8n` image, recreate container, keep `n8n_data` volume and common env flags. | `./updaten8n.sh` |
| `updaters/updateAItools.sh` | Global install/update for a few AI CLIs (`@openai/codex`, `@google/gemini-cli`, `opencode-ai`, Claude installer). | `./updaters/updateAItools.sh` |
| `model-runners/nemotron-1m-24gb.sh` | Launch `llama-server` with Nemotron GGUF config and large context window. | `./model-runners/nemotron-1m-24gb.sh` |
| `mongo-scripts/mongo-backup.py` | MongoDB backup script with interactive database picker (curses) or CLI mode. | `cd mongo-scripts && uv run mongo-backup.py --url <mongo-url>` |
| `notes/scrape_twitter_repos.md` | Scratch note containing a sample Playwright-based scraping approach. | Open/read file |

## Folder Layout

- `model-runners/`: scripts for running local/hosted model servers
- `mongo-scripts/`: Python-based Mongo helper tooling
- `updaters/`: update/install scripts for dev tools
- `notes/`: random notes and experiments

## Quick Usage

### Update n8n container

```bash
./updaten8n.sh
```

### Update AI CLI tools

```bash
./updaters/updateAItools.sh
```

### Run Nemotron via llama-server

```bash
./model-runners/nemotron-1m-24gb.sh
```

### Run Mongo backup tool

```bash
cd mongo-scripts
uv sync
uv run mongo-backup.py --url mongodb://localhost:27017
```

For full Mongo backup options, see `mongo-scripts/README.md`.

## Maintenance Rule

When adding or changing a helper script:

1. Update this `README.md` inventory row.
2. Add a one-line purpose and one run command.
3. Note prerequisites if the script needs external tooling.
