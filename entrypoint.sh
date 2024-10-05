set -e

sleep 5

if [ -f /app/seemyfamily.dump ]; then
  echo "Restoring the database from the dump file..."
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v /app/seemyfamily.dump
else
  echo "No dump file found, skipping restore."
fi

exec "$@"
