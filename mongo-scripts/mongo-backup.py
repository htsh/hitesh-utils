#!/usr/bin/env python3
"""
MongoDB Backup Tool with Interactive Database Selection
Provides an ncurses-based checkbox UI for selecting databases to backup.
"""

import curses
import sys
import subprocess
import argparse
import json
import os
import zipfile
import shutil
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


class MongoBackupTool:
    def __init__(self, mongo_url, output_dir='./backups', exclude_system_dbs=True):
        self.mongo_url = mongo_url
        self.output_dir = output_dir
        self.exclude_system_dbs = exclude_system_dbs
        self.system_dbs = ['admin', 'local', 'config']

    def get_databases(self):
        """Connect to MongoDB and retrieve list of databases."""
        try:
            client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=5000)
            # Test connection
            client.admin.command('ping')

            databases = client.list_database_names()

            # Filter out system databases if requested
            if self.exclude_system_dbs:
                databases = [db for db in databases if db not in self.system_dbs]

            client.close()
            return sorted(databases)

        except ConnectionFailure as e:
            print(f"Error: Failed to connect to MongoDB: {e}", file=sys.stderr)
            sys.exit(1)
        except OperationFailure as e:
            print(f"Error: MongoDB operation failed: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def checkbox_menu(self, stdscr, databases):
        """Display interactive checkbox menu for database selection."""
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()

        # Initialize selection state (all selected by default)
        selected = [True] * len(databases)
        current_row = 0

        # Color setup
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Header
            title = "MongoDB Backup - Select Databases"
            stdscr.attron(curses.A_BOLD)
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.A_BOLD)

            # Instructions
            instructions = [
                "↑/↓ or k/j: Navigate  |  Space: Toggle  |  a: Select All  |  n: Select None  |  Enter: Confirm  |  q: Quit"
            ]
            stdscr.addstr(1, 0, instructions[0][:width-1], curses.color_pair(3))
            stdscr.addstr(2, 0, "─" * (width - 1))

            # Database list
            start_row = 4
            max_visible = height - start_row - 3

            # Calculate scroll offset
            if current_row < max_visible // 2:
                scroll_offset = 0
            elif current_row > len(databases) - max_visible // 2:
                scroll_offset = max(0, len(databases) - max_visible)
            else:
                scroll_offset = current_row - max_visible // 2

            visible_databases = databases[scroll_offset:scroll_offset + max_visible]

            for idx, db in enumerate(visible_databases):
                actual_idx = idx + scroll_offset
                checkbox = "[✓]" if selected[actual_idx] else "[ ]"
                line = f"{checkbox} {db}"

                y_pos = start_row + idx

                if actual_idx == current_row:
                    # Highlight current row
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y_pos, 2, line[:width-3])
                    stdscr.attroff(curses.color_pair(1))
                else:
                    if selected[actual_idx]:
                        stdscr.addstr(y_pos, 2, checkbox, curses.color_pair(2))
                        stdscr.addstr(y_pos, 2 + len(checkbox) + 1, db)
                    else:
                        stdscr.addstr(y_pos, 2, line[:width-3])

            # Footer with stats
            selected_count = sum(selected)
            footer = f"Selected: {selected_count}/{len(databases)} databases"
            stdscr.addstr(height - 2, 0, "─" * (width - 1))
            stdscr.addstr(height - 1, (width - len(footer)) // 2, footer, curses.color_pair(2))

            stdscr.refresh()

            # Handle input
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return None

            if key in [ord('q'), ord('Q'), 27]:  # q, Q, or ESC
                return None
            elif key in [ord(' ')]:  # Space - toggle selection
                selected[current_row] = not selected[current_row]
            elif key in [ord('a'), ord('A')]:  # Select all
                selected = [True] * len(databases)
            elif key in [ord('n'), ord('N')]:  # Select none
                selected = [False] * len(databases)
            elif key in [curses.KEY_UP, ord('k')]:  # Move up
                current_row = max(0, current_row - 1)
            elif key in [curses.KEY_DOWN, ord('j')]:  # Move down
                current_row = min(len(databases) - 1, current_row + 1)
            elif key in [curses.KEY_PPAGE]:  # Page up
                current_row = max(0, current_row - max_visible)
            elif key in [curses.KEY_NPAGE]:  # Page down
                current_row = min(len(databases) - 1, current_row + max_visible)
            elif key in [ord('\n'), curses.KEY_ENTER, 10, 13]:  # Enter
                selected_dbs = [db for idx, db in enumerate(databases) if selected[idx]]
                return selected_dbs if selected_dbs else None

    def generate_human_readable_filename(self):
        """Generate a human-readable filename for the zip archive."""
        now = datetime.now()
        month = now.strftime('%B').lower()  # Full month name in lowercase
        day = now.day
        year = now.year
        hour = now.hour
        minute = now.minute

        # Convert to 12-hour format
        if hour == 0:
            hour_12 = 12
            period = 'am'
        elif hour < 12:
            hour_12 = hour
            period = 'am'
        elif hour == 12:
            hour_12 = 12
            period = 'pm'
        else:
            hour_12 = hour - 12
            period = 'pm'

        return f"{month}_{day}_{year}_{hour_12}_{minute:02d}_{period}.zip"

    def create_zip_archive(self, source_dir, zip_filename):
        """Create a zip archive of the backup directory."""
        zip_path = os.path.join(self.output_dir, zip_filename)

        try:
            print(f"\n  → Creating zip archive: {zip_filename}...", end=' ', flush=True)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through the source directory
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate the archive name (relative path from source_dir parent)
                        arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                        zipf.write(file_path, arcname)
            print("✓")
            return zip_path
        except Exception as e:
            print(f"✗")
            print(f"    Error creating zip: {e}", file=sys.stderr)
            return None

    def run_mongodump(self, database, timestamp):
        """Execute mongodump for a specific database."""
        output_path = os.path.join(self.output_dir, timestamp, database)

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        cmd = [
            'mongodump',
            '--uri', self.mongo_url,
            '--db', database,
            '--out', os.path.join(self.output_dir, timestamp)
        ]

        try:
            print(f"  → Backing up '{database}'...", end=' ', flush=True)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print("✓")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗")
            print(f"    Error: {e.stderr}", file=sys.stderr)
            return False
        except FileNotFoundError:
            print(f"✗")
            print(f"    Error: 'mongodump' command not found. Please install MongoDB Database Tools.", file=sys.stderr)
            return False

    def backup_databases(self, databases, create_zip=False):
        """Backup selected databases."""
        if not databases:
            print("No databases selected for backup.")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(self.output_dir, timestamp)

        print(f"\n{'='*60}")
        print(f"Starting backup of {len(databases)} database(s)")
        print(f"Timestamp: {timestamp}")
        print(f"Output directory: {os.path.abspath(backup_dir)}")
        print(f"{'='*60}\n")

        success_count = 0
        failed_dbs = []

        for db in databases:
            if self.run_mongodump(db, timestamp):
                success_count += 1
            else:
                failed_dbs.append(db)

        # Handle zip creation if requested
        zip_path = None
        if create_zip and success_count > 0:
            zip_filename = self.generate_human_readable_filename()
            zip_path = self.create_zip_archive(backup_dir, zip_filename)

            if zip_path:
                # Clean up the uncompressed backup directory
                try:
                    print(f"  → Cleaning up uncompressed files...", end=' ', flush=True)
                    shutil.rmtree(backup_dir)
                    print("✓")
                except Exception as e:
                    print(f"✗")
                    print(f"    Warning: Could not remove temporary backup directory: {e}", file=sys.stderr)

        # Summary
        print(f"\n{'='*60}")
        print(f"Backup Complete!")
        print(f"  ✓ Successful: {success_count}/{len(databases)}")
        if failed_dbs:
            print(f"  ✗ Failed: {len(failed_dbs)} - {', '.join(failed_dbs)}")

        if create_zip and zip_path:
            print(f"  Location: {os.path.abspath(zip_path)}")
        else:
            print(f"  Location: {os.path.abspath(backup_dir)}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='MongoDB Backup Tool with Interactive Database Selection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (with checkbox UI)
  %(prog)s --url mongodb://localhost:27017

  # Non-interactive mode (for cron jobs)
  %(prog)s --url mongodb://localhost:27017 --databases mydb1 mydb2

  # Backup all databases (including system databases)
  %(prog)s --url mongodb://localhost:27017 --all

  # Custom output directory
  %(prog)s --url mongodb://user:pass@host:27017 --output /backups/mongo
        """
    )

    parser.add_argument(
        '--url',
        required=True,
        help='MongoDB connection URL (e.g., mongodb://localhost:27017)'
    )
    parser.add_argument(
        '--databases',
        nargs='+',
        help='Specific databases to backup (skips interactive mode)'
    )
    parser.add_argument(
        '--output',
        default='./backups',
        help='Output directory for backups (default: ./backups)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Include system databases (admin, local, config)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available databases and exit'
    )
    parser.add_argument(
        '--zip',
        action='store_true',
        help='Create a zip archive of the backup and clean up uncompressed files'
    )

    args = parser.parse_args()

    # Create backup tool instance
    tool = MongoBackupTool(
        mongo_url=args.url,
        output_dir=args.output,
        exclude_system_dbs=not args.all
    )

    # Get list of databases
    databases = tool.get_databases()

    if not databases:
        print("No databases found.")
        sys.exit(0)

    # List mode
    if args.list:
        print(f"Available databases ({len(databases)}):")
        for db in databases:
            print(f"  • {db}")
        sys.exit(0)

    # Determine which databases to backup
    if args.databases:
        # Non-interactive mode
        selected_databases = args.databases
        # Validate that specified databases exist
        invalid_dbs = [db for db in selected_databases if db not in databases]
        if invalid_dbs:
            print(f"Error: The following databases were not found: {', '.join(invalid_dbs)}", file=sys.stderr)
            print(f"Available databases: {', '.join(databases)}")
            sys.exit(1)
    else:
        # Interactive mode
        try:
            selected_databases = curses.wrapper(tool.checkbox_menu, databases)
        except Exception as e:
            print(f"Error in interactive mode: {e}", file=sys.stderr)
            sys.exit(1)

        if selected_databases is None:
            print("\nBackup cancelled.")
            sys.exit(0)

    # Perform backup
    tool.backup_databases(selected_databases, create_zip=args.zip)


if __name__ == '__main__':
    main()
