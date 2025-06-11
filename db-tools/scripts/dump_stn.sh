psql -U postgres -h 10.8.7.59 -p 5433 -d weather \
  -t -A -F"," \
  -c "SELECT * FROM observations_station ORDER BY id;" > station-old.csv

