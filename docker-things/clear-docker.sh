#!/usr/bin/env bash
set -euo pipefail

dry_run=false

usage() {
  echo "Usage: $0 [--dry-run|-n]"
}

if [ "${1-}" = "--dry-run" ] || [ "${1-}" = "-n" ]; then
  dry_run=true
elif [ "${1-}" = "--help" ] || [ "${1-}" = "-h" ]; then
  usage
  exit 0
elif [ "${1-}" != "" ]; then
  echo "Unknown option: $1" >&2
  usage >&2
  exit 1
fi

run_or_print() {
  if $dry_run; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

# Stop running containers.
running_containers="$(docker ps -q)"
if [ -n "$running_containers" ]; then
  run_or_print docker kill $running_containers
fi

# Remove all containers.
all_containers="$(docker ps -a -q)"
if [ -n "$all_containers" ]; then
  run_or_print docker rm $all_containers
fi

# Remove all volumes.
all_volumes="$(docker volume ls -q)"
if [ -n "$all_volumes" ]; then
  run_or_print docker volume rm $all_volumes
fi

# Remove all images.
all_images="$(docker images -q)"
if [ -n "$all_images" ]; then
  run_or_print docker rmi $all_images
fi
