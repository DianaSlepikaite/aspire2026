#!/bin/bash
# Run the Employee Conversation Service schema in PostgreSQL.
# This creates the employee_documents and employee_profiles tables.
#
# Usage:
#   ./run_employee_schema.sh                    # uses .env in backend/
#   ./run_employee_schema.sh mydb host 5432 user pass   # explicit args
#
# Prerequisites:
#   - Database employee_conversation_db (or your DB name) must already exist.
#   - psql must be installed and on PATH.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
SCHEMA_FILE="$SCRIPT_DIR/employee_conversation_service/schema.sql"

if [[ ! -f "$SCHEMA_FILE" ]]; then
  echo "Schema file not found: $SCHEMA_FILE"
  exit 1
fi

if [[ -n "$4" ]]; then
  # Explicit: DB_NAME HOST PORT USER PASSWORD
  DB_NAME="${1:-employee_conversation_db}"
  DB_HOST="${2:-localhost}"
  DB_PORT="${3:-5432}"
  DB_USER="${4:-postgres}"
  DB_PASSWORD="${5:-}"
else
  # Load from .env if present
  if [[ -f .env ]]; then
    export $(grep -v '^#' .env | xargs)
  fi
  DB_NAME="${EMPLOYEE_DB_NAME:-employee_conversation_db}"
  DB_HOST="${EMPLOYEE_DB_HOST:-$DB_HOST}"
  DB_HOST="${DB_HOST:-localhost}"
  DB_PORT="${EMPLOYEE_DB_PORT:-$DB_PORT}"
  DB_PORT="${DB_PORT:-5432}"
  DB_USER="${EMPLOYEE_DB_USER:-$DB_USER}"
  DB_USER="${DB_USER:-postgres}"
  DB_PASSWORD="${EMPLOYEE_DB_PASSWORD:-$DB_PASSWORD}"
fi

export PGPASSWORD="$DB_PASSWORD"
echo "Running schema in database: $DB_NAME on $DB_HOST:$DB_PORT as $DB_USER"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"
unset PGPASSWORD
echo "Done. Tables employee_documents and employee_profiles should now exist in $DB_NAME."
