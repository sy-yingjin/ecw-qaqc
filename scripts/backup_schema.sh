#!/bin/sh

TIMESTAMP=$(date +%Y%m%d%H%M)
BAK_DIR=/home/modelman/workdir/mo_wcr/db_bak/bak/schema
PG_OPTS="-U postgres -h 10.8.6.69 -p 5433 -d weather -Cs"

pg_dump ${PG_OPTS} > ${BAK_DIR}/weather_schema_${TIMESTAMP}.sql

