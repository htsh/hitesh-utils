# MongoDB Backup Tool

An interactive terminal-based MongoDB backup tool with a checkbox UI for selecting databases to backup.

## Features

- **Interactive ncurses UI** with checkbox selection
- Navigate with arrow keys or vim-style (j/k)
- Select/deselect individual databases or all at once
- Automatic filtering of system databases (admin, local, config)
- Non-interactive mode for cron jobs
- Date-stamped backup directories
- Progress indicators and error handling

## Prerequisites

1. **Python 3.8+** (with curses support, typically included on Linux/macOS)
2. **UV** - Fast Python package manager
   ```bash
   # Install UV (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or with pip
   pip install uv

   # Or with Homebrew
   brew install uv
   ```
3. **MongoDB Database Tools** - `mongodump` must be installed and in PATH
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb-database-tools

   # macOS
   brew install mongodb-database-tools

   # Or download from: https://www.mongodb.com/try/download/database-tools
   ```

## Installation

```bash
# Clone or download the script
git clone <your-repo-url>
cd mongo-scripts

# Install dependencies with UV
uv sync

# Make script executable
chmod +x mongo-backup.py
```

## Usage

### Interactive Mode (with checkbox UI)

Perfect for manual backups where you want to select databases visually:

```bash
# Using UV (recommended)
uv run mongo-backup.py --url mongodb://localhost:27017

# Or directly (if dependencies are installed)
./mongo-backup.py --url mongodb://localhost:27017
```

**UI Controls:**
- `↑/↓` or `j/k`: Navigate up/down
- `Space`: Toggle checkbox for current database
- `a`: Select all databases
- `n`: Deselect all databases
- `Enter`: Confirm selection and start backup
- `q` or `ESC`: Cancel and exit

### Non-Interactive Mode (for cron jobs)

Specify databases directly via command line:

```bash
uv run mongo-backup.py --url mongodb://localhost:27017 --databases mydb1 mydb2 mydb3
```

### List Available Databases

```bash
uv run mongo-backup.py --url mongodb://localhost:27017 --list
```

### Include System Databases

By default, system databases (admin, local, config) are excluded. To include them:

```bash
uv run mongo-backup.py --url mongodb://localhost:27017 --all
```

### Custom Output Directory

```bash
uv run mongo-backup.py --url mongodb://localhost:27017 --output /var/backups/mongo
```

## MongoDB Connection URLs

The tool supports all standard MongoDB connection string formats:

```bash
# Local MongoDB
mongodb://localhost:27017

# With authentication
mongodb://username:password@localhost:27017

# Remote MongoDB
mongodb://user:pass@remote-host:27017

# MongoDB Atlas or other cloud providers
mongodb+srv://user:pass@cluster.mongodb.net

# With authentication database
mongodb://user:pass@host:27017/?authSource=admin

# Replica set
mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=myReplSet
```

## Cron Job Setup

For automated backups, use non-interactive mode with UV:

### Example 1: Backup specific databases daily at 2 AM

```bash
# Edit crontab
crontab -e

# Add this line (using uv run)
0 2 * * * cd /path/to/mongo-scripts && /usr/local/bin/uv run mongo-backup.py --url mongodb://user:pass@host:27017 --databases production analytics --output /backups/mongo >> /var/log/mongo-backup.log 2>&1
```

### Example 2: Backup all databases weekly

```bash
# Every Sunday at 3 AM
0 3 * * 0 cd /path/to/mongo-scripts && /usr/local/bin/uv run mongo-backup.py --url mongodb://localhost:27017 --databases db1 db2 db3 --output /backups/mongo
```

### Example 3: Create a wrapper script for cron

Create a file `backup-cron.sh`:

```bash
#!/bin/bash
# MongoDB backup script for cron

# Change to script directory
cd /path/to/mongo-scripts || exit 1

MONGO_URL="mongodb://user:password@host:27017/?authSource=admin"
DATABASES="production analytics logs"
OUTPUT_DIR="/var/backups/mongo"
LOG_FILE="/var/log/mongo-backup.log"

# Run backup with UV
/usr/local/bin/uv run mongo-backup.py \
    --url "$MONGO_URL" \
    --databases $DATABASES \
    --output "$OUTPUT_DIR" \
    >> "$LOG_FILE" 2>&1

# Optional: Clean up old backups (keep last 7 days)
find "$OUTPUT_DIR" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null
```

Make it executable and add to crontab:
```bash
chmod +x backup-cron.sh
crontab -e
# Add: 0 2 * * * /path/to/backup-cron.sh
```

**Note:** Find the UV binary location with `which uv` (usually `/usr/local/bin/uv` or `~/.cargo/bin/uv`)

## Output Structure

Backups are organized by timestamp:

```
backups/
├── 20250121_140530/
│   ├── database1/
│   │   └── (BSON files)
│   └── database2/
│       └── (BSON files)
└── 20250122_020015/
    ├── database1/
    └── database2/
```

## Restoring Backups

Use `mongorestore` to restore databases:

```bash
# Restore specific database
mongorestore --uri mongodb://localhost:27017 --db mydb backups/20250121_140530/mydb

# Restore all databases from a backup
mongorestore --uri mongodb://localhost:27017 backups/20250121_140530/
```

## Troubleshooting

### "mongodump command not found"
Install MongoDB Database Tools (see Prerequisites section)

### "Failed to connect to MongoDB"
- Verify the MongoDB URL is correct
- Check if MongoDB is running
- Verify network connectivity and firewall rules
- Check authentication credentials

### Terminal UI looks broken
- Ensure your terminal supports curses (most Linux/macOS terminals do)
- Try a different terminal emulator
- Check terminal size is adequate (minimum 80x24 recommended)

### Permission denied when writing backups
- Ensure the output directory exists and is writable
- Use `--output` to specify a directory you have write access to

## Security Notes

- **Never hardcode credentials** in scripts or cron jobs
- Use environment variables or secure credential management:
  ```bash
  export MONGO_URL="mongodb://user:pass@host:27017"
  ./mongo-backup.py --url "$MONGO_URL"
  ```
- Ensure backup directories have appropriate permissions (600 or 700)
- Consider encrypting sensitive backups
- Rotate and test backups regularly

## Advanced Usage

### Backup from remote server via SSH

```bash
ssh backup-server 'cd /path/to/mongo-scripts && uv run mongo-backup.py --url mongodb://dbhost:27017 --databases db1 db2'
```

### Combine with compression

```bash
uv run mongo-backup.py --url mongodb://localhost:27017 --databases mydb --output /tmp/backup
tar -czf mongo-backup-$(date +%Y%m%d).tar.gz -C /tmp/backup .
```

### Backup and upload to cloud storage

```bash
#!/bin/bash
cd /path/to/mongo-scripts || exit 1
uv run mongo-backup.py --url "$MONGO_URL" --databases db1 db2 --output /tmp/backup
aws s3 sync /tmp/backup s3://my-backup-bucket/mongo/
rm -rf /tmp/backup
```

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!
