#!/bin/sh
set -e

# Ensure uploads directory structure exists and is owned by appuser
mkdir -p /app/uploads/cvs
chown -R appuser:appuser /app/uploads

# If running as root, drop privileges and exec command as appuser
if [ "$(id -u)" = '0' ]; then
    exec gosu appuser "$@"
fi

exec "$@"
