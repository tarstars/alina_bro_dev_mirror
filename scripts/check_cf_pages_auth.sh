#!/usr/bin/env bash
set -euo pipefail

API_BASE="https://api.cloudflare.com/client/v4"

required=(
  CLOUDFLARE_API_TOKEN
  CLOUDFLARE_ACCOUNT_ID
  CF_PAGES_PROJECT_NAME
)

missing=()
for v in "${required[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    missing+=("$v")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "Missing required env vars: ${missing[*]}"
  echo
  echo "Usage:"
  echo "  CLOUDFLARE_API_TOKEN=... CLOUDFLARE_ACCOUNT_ID=... CF_PAGES_PROJECT_NAME=... ./scripts/check_cf_pages_auth.sh"
  exit 2
fi

redact() {
  local value="$1"
  local n=${#value}
  if (( n <= 8 )); then
    printf '***'
  else
    printf '%s***%s' "${value:0:4}" "${value:n-4:4}"
  fi
}

call_api() {
  local endpoint="$1"
  local tmp
  tmp=$(mktemp)
  local code
  code=$(curl -sS -o "$tmp" -w "%{http_code}" \
    -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
    -H "Content-Type: application/json" \
    "${API_BASE}${endpoint}")

  API_HTTP_CODE="$code"
  API_BODY=$(cat "$tmp")
  rm -f "$tmp"
}

json_get() {
  local expr="$1"
  python3 - "$expr" <<'PY' <<<"${API_BODY}"
import json
import sys

expr = sys.argv[1]
try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    raise SystemExit(0)

if expr == "success":
    print("true" if data.get("success") else "false")
elif expr == "errors":
    errs = data.get("errors") or []
    if not errs:
        print("none")
    else:
        print("; ".join(f"{e.get('code')}: {e.get('message')}" for e in errs))
elif expr == "token_status":
    print((data.get("result") or {}).get("status", ""))
elif expr == "token_id":
    print((data.get("result") or {}).get("id", ""))
elif expr == "account_name":
    print((data.get("result") or {}).get("name", ""))
elif expr == "project_name":
    print((data.get("result") or {}).get("name", ""))
elif expr == "project_subdomain":
    print((data.get("result") or {}).get("subdomain", ""))
elif expr == "projects":
    items = data.get("result") or []
    names = [x.get("name", "") for x in items if isinstance(x, dict)]
    print(", ".join([x for x in names if x]) or "none")
else:
    print("")
PY
}

print_header() {
  local title="$1"
  echo
  echo "== $title =="
}

echo "Cloudflare Pages Auth Diagnostic"
echo "Token:      $(redact "$CLOUDFLARE_API_TOKEN")"
echo "Account ID: ${CLOUDFLARE_ACCOUNT_ID}"
echo "Project:    ${CF_PAGES_PROJECT_NAME}"

print_header "1) Verify API token"
call_api "/user/tokens/verify"
if [[ "$API_HTTP_CODE" != "200" || "$(json_get success)" != "true" ]]; then
  echo "FAIL: token verification failed"
  echo "HTTP: $API_HTTP_CODE"
  echo "Errors: $(json_get errors)"
  exit 1
fi

echo "OK: token is valid"
echo "Token status: $(json_get token_status)"
echo "Token id: $(redact "$(json_get token_id)")"

print_header "2) Check account access"
call_api "/accounts/${CLOUDFLARE_ACCOUNT_ID}"
if [[ "$API_HTTP_CODE" != "200" || "$(json_get success)" != "true" ]]; then
  echo "FAIL: account access failed"
  echo "HTTP: $API_HTTP_CODE"
  echo "Errors: $(json_get errors)"
  echo "Hint: wrong CLOUDFLARE_ACCOUNT_ID or token has no access to this account."
  exit 1
fi

echo "OK: account is accessible"
echo "Account name: $(json_get account_name)"

print_header "3) Check Pages project access"
call_api "/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects/${CF_PAGES_PROJECT_NAME}"
if [[ "$API_HTTP_CODE" != "200" || "$(json_get success)" != "true" ]]; then
  echo "FAIL: Pages project access failed"
  echo "HTTP: $API_HTTP_CODE"
  echo "Errors: $(json_get errors)"

  echo
  echo "Checking available Pages projects in this account..."
  call_api "/accounts/${CLOUDFLARE_ACCOUNT_ID}/pages/projects?per_page=50"
  if [[ "$API_HTTP_CODE" == "200" && "$(json_get success)" == "true" ]]; then
    echo "Projects: $(json_get projects)"
    echo "Hint: if your project is absent, fix CF_PAGES_PROJECT_NAME or create the Pages project in this account."
  else
    echo "Could not list projects (HTTP $API_HTTP_CODE): $(json_get errors)"
    echo "Hint: token may be missing Pages permissions."
  fi

  exit 1
fi

echo "OK: Pages project is accessible"
echo "Project name: $(json_get project_name)"
echo "Subdomain:    $(json_get project_subdomain)"

echo

echo "All checks passed. These three variables are valid for Pages deploy."
