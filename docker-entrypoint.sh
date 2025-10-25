#!/usr/bin/env bash
set -e

echo "Python:" $(python -V)
echo "Waiting for Postgres at $POSTGRES_HOST:$POSTGRES_PORT ..."

until python - <<'PY'
import os, time, psycopg2
for _ in range(60):
    try:
        psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        ).close()
        raise SystemExit(0)
    except Exception:
        time.sleep(1)
raise SystemExit(1)
PY
do
  echo "waiting..."
  sleep 1
done

python manage.py collectstatic --noinput
python manage.py migrate --noinput

python manage.py runserver 0.0.0.0:8000