#!/usr/bin/env bash

TABLE_NAME=observations_observationraw

[ -z "$1" ] && exit
yyyy=$1

[ -z "$2" ] && exit
mm=$2

start_date="$yyyy-$mm-01 00:00:00+08"
end_date=$(date -d "$start_date + 1 month - 1 day" "+%Y-%m-%d 23:59:59+08")

echo "deleting $TABLE_NAME $yyyy-$mm..."
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" \
  -c "DELETE FROM $TABLE_NAME WHERE timestamp BETWEEN '$start_date' AND '$end_date';"
