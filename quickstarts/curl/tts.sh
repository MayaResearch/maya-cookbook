#!/usr/bin/env bash
# Run from this folder. All secrets stay in curl's stdin, not its argv or a file.
set -euo pipefail
set +x
cd -- "$(dirname -- "$0")"
: "${MAYA_API_KEY:?Set MAYA_API_KEY in your environment}"
output=${1:-output.wav}
if [[ -e "$output" ]]; then echo "Output exists; choose a new filename" >&2; exit 1; fi
if [[ "$MAYA_API_KEY" == *$'\n'* || "$MAYA_API_KEY" == *$'\r'* || "$MAYA_API_KEY" == *'"'* || "$MAYA_API_KEY" == *'\'* ]]; then
  echo 'Invalid key format' >&2; exit 1
fi
python3 verify.py --request request.json
task_tmp=$(mktemp -d)
cleanup() { rm -f -- "$task_tmp/body" "$task_tmp/headers"; rmdir -- "$task_tmp"; }
trap cleanup EXIT
# No redirects and no retries. A partial speech request must not be replayed.
code=$(printf 'header = "Authorization: Bearer %s"\n' "$MAYA_API_KEY" |
  curl --config - --silent --show-error --max-time 60 --connect-timeout 15 \
    --proto '=https' --request POST 'https://tts.mayaresearch.ai/v1/tts' \
    --header 'Content-Type: application/json' --user-agent 'maya-cookbook/0.1' \
    --data-binary @request.json --dump-header "$task_tmp/headers" \
    --output "$task_tmp/body" --write-out '%{http_code}')
if [[ "$code" != 200 ]]; then
  echo "Maya HTTP $code; no audio file written. See troubleshooting." >&2; exit 1
fi
python3 verify.py --headers "$task_tmp/headers" --pcm "$task_tmp/body" --output "$output"
