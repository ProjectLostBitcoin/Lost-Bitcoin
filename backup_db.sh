#!/bin/sh
# Back up the Lost Bitcoin SQLite database using SQLite's online-backup
# API (safe while the server is running). Keeps the newest 14 copies.
#
# Usage:  DB=/data/lost_bitcoin.db BACKUP_DIR=/data/backups ./backup_db.sh
# Run it from the host's scheduler (or manually) — and copy backups OFF
# the host regularly; a backup that lives only beside the original is
# not a backup.
set -eu

DB="${DB:-/data/lost_bitcoin.db}"
BACKUP_DIR="${BACKUP_DIR:-/data/backups}"
mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
python3 - "$DB" "$BACKUP_DIR/lost_bitcoin-$STAMP.db" <<'PY'
import sqlite3, sys
src = sqlite3.connect(sys.argv[1])
dst = sqlite3.connect(sys.argv[2])
with dst:
    src.backup(dst)
dst.close(); src.close()
print("backed up to", sys.argv[2])
PY

ls -1t "$BACKUP_DIR"/lost_bitcoin-*.db | tail -n +15 | xargs -r rm -f
