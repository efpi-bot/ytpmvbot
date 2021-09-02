#!/bin/sh -eu
# YTPMVBot entrypoint script for Docker
BOT_DIRECTORY=$(dirname $0)
TOKENFILE="$BOT_DIRECTORY/key"

die() {
    echo "[ERR] $@" >&2
    exit 1
}

cd "$BOT_DIRECTORY"

[ -z "${TOKEN+x}" ] && die "\$TOKEN is not set." || echo "\$TOKEN is set"
[ ${#TOKEN} -ne 59 ] && die "Invalid Discord token format."
[ -s "$TOKENFILE" ] && echo "Token file is not empty and will be overwritten." >&2

echo "$TOKEN" > "$TOKENFILE"

echo "Starting bot..."
echo $$ > /opt/ytpmvbot/bot.pid; exec "$@"