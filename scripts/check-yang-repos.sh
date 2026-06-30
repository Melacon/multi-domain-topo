#!/usr/bin/env bash
# Verifies that local external YANG Git repositories match yang-repos.lock.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCK_FILE="${YANG_REPOS_LOCK:-$REPO_ROOT/yang-repos.lock}"

if [ ! -f "$LOCK_FILE" ]; then
  echo "ERROR: lock file not found: $LOCK_FILE"
  exit 1
fi

# shellcheck source=/dev/null
. "$LOCK_FILE"

status=0

resolve_ref() {
  local repo_dir="$1"
  local ref="$2"
  local candidate

  if [[ "$ref" =~ ^[0-9a-fA-F]{40}$ ]] && git -C "$repo_dir" cat-file -e "$ref^{commit}" 2>/dev/null; then
    echo "$ref"
    return 0
  fi

  for candidate in "refs/tags/$ref" "refs/remotes/origin/$ref" "refs/heads/$ref" "$ref"; do
    if git -C "$repo_dir" rev-parse --verify --quiet "$candidate^{commit}" >/dev/null; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

check_repo() {
  local name="$1"
  local repo_dir="$2"
  local expected_url="$3"
  local expected_ref="$4"
  local locked_commit="${5:-}"

  echo "[$name] $repo_dir"

  if [ ! -d "$repo_dir/.git" ]; then
    echo "  ERROR: repository is missing; run ./setup-yang-repos.sh"
    status=1
    return
  fi

  local actual_url
  actual_url="$(git -C "$repo_dir" remote get-url origin 2>/dev/null || true)"
  if [ "$actual_url" != "$expected_url" ]; then
    echo "  WARN: origin is '$actual_url', expected '$expected_url'"
  fi

  local dirty
  dirty="$(git -C "$repo_dir" status --porcelain)"
  if [ -n "$dirty" ]; then
    echo "  ERROR: working tree has local changes"
    git -C "$repo_dir" status --short
    status=1
  fi

  local resolved_ref
  if ! resolved_ref="$(resolve_ref "$repo_dir" "$expected_ref")"; then
    echo "  ERROR: expected ref not available locally: $expected_ref"
    echo "  Run ./setup-yang-repos.sh or check whether the ref exists upstream."
    status=1
    return
  fi

  local expected_commit
  expected_commit="$(git -C "$repo_dir" rev-parse "$resolved_ref^{commit}")"
  if [ -n "$locked_commit" ] && [ "$expected_commit" != "$locked_commit" ]; then
    echo "  ERROR: $expected_ref resolves to $expected_commit"
    echo "         locked commit is $locked_commit"
    status=1
    return
  fi

  local actual_commit
  actual_commit="$(git -C "$repo_dir" rev-parse HEAD)"

  if [ "$actual_commit" != "$expected_commit" ]; then
    echo "  ERROR: HEAD is $actual_commit"
    echo "         expected $expected_commit ($expected_ref -> $resolved_ref)"
    status=1
  else
    local described
    described="$(git -C "$repo_dir" describe --tags --always --dirty)"
    echo "  OK: $described ($actual_commit)"
  fi
}

check_repo "yang" "$REPO_ROOT/yang-repos/yang" "$YANG_MODELS_URL" "$YANG_MODELS_REF"
check_repo "OpenROADM" "$REPO_ROOT/yang-repos/OpenROADM_MSA_Public" "$OPENROADM_URL" "$OPENROADM_REF"
check_repo "MnS" "$REPO_ROOT/yang-repos/MnS" "$MNS_URL" "$MNS_REF" "$MNS_COMMIT"

if [ "$status" -ne 0 ]; then
  echo ""
  echo "YANG repository check failed."
  exit "$status"
fi

echo ""
echo "YANG repository check passed."
