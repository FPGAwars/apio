#!/usr/bin/env bash

# Skeleton script to for one time cleanup of repo's releases and tag.
# It generates a bash script with commented out commands to delete each
# release and each tag. Uncomment the ones you want to delete and run
# the generated shell script.

set -euo pipefail

# ------------------------------------------------------------
# Usage: ./repo-cleaner-gen.sh <owner/repo>
# Example: ./repo-cleaner-gen.sh zapta/apio-vscode
# ------------------------------------------------------------

if [[ $# -ne 1 ]]; then
  echo "Error: Please provide exactly one argument: owner/repo"
  echo "Example: $0 zapta/apio-vscode"
  exit 1
fi

REPO="$1"

cat <<EOF
#!/usr/bin/env bash
set -euo pipefail

REPO="$REPO"

delete_release() {
  local tag="\$1"
  echo "Deleting release: \$tag"
  gh release delete "\$tag" --yes --repo "\$REPO" 2>/dev/null || echo "  → Release already gone or not accessible"
}

delete_tag() {
  local tag="\$1"
  echo "Deleting tag: \$tag"
  gh api --method DELETE "/repos/\$REPO/git/refs/tags/\$tag" --silent 2>/dev/null || echo "  → Tag already gone or not accessible"
}

delete_release_and_tag() {
  local tag="\$1"
  delete_release "\$tag"
  delete_tag "\$tag"
}

echo "DRY RUN — No deletions will happen until you uncomment the lines below"
echo "Repo: $REPO"
echo "========================================================================"
echo
echo "# 1. Releases + their tags (release first, then tag)"
echo

EOF

# Step 1: For every release → delete release + tag (in that order)
gh release list --repo "$REPO" --limit 1000 --json tagName -q '.[].tagName' |
  sort -V |
  while read -r tag; do
    [[ -n "$tag" ]] || continue
    echo "# delete_release_and_tag  \"$tag\""
  done

# Step 2: All tags that are NOT attached to any release
cat <<'EOF'

echo
echo "# 2. Orphaned / unused tags (no associated release)"
echo

EOF

# Get all tags without a release
comm -23 \
  <(gh api "repos/$REPO/tags?per_page=100" --paginate --jq '.[].name' | sort -u) \
  <(gh release list --repo "$REPO" --limit 1000 --json tagName -q '.[].tagName' | sort -u) |
  while read -r tag; do
    [[ -n "$tag" ]] && echo "# delete_tag  \"$tag\""
  done

cat <<'EOF'

echo
EOF