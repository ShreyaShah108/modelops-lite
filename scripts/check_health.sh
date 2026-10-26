#!/usr/bin/env bash

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8001/health}"

echo "Checking API health at: $HEALTH_URL"

if HTTP_STATUS=$(curl --silent --show-error \
    --output /dev/null \
    --write-out "%{http_code}" \
    --max-time 5 \
    "$HEALTH_URL"); then

    if [ "$HTTP_STATUS" = "200" ]; then
        echo "Health check passed (HTTP $HTTP_STATUS)."
        exit 0
    else
        echo "Health check failed (HTTP $HTTP_STATUS)."
        exit 1
    fi
else
    echo "Health check failed: API unavailable or request timed out."
    exit 1
fi
