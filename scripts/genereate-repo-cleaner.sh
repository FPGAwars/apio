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
  gh release delete "\$tag" --yes --repo "\$REPO" 2>/dev/null || echo "  → Release already gone or not found"
}

delete_tag() {
  local tag="\$1"
  echo "Deleting tag: \$tag"
  gh api --method DELETE "/repos/\$REPO/git/refs/tags/\$tag" --silent 2>/dev/null || echo "  → Tag already gone or not found"
}

echo "DRY RUN — No deletions will happen until you uncomment the lines below"
echo "Repo: \$REPO"
echo "========================================================================"
EOF

# Releases — commented out
echo
echo "# Releases (uncomment to delete)"
gh release list --repo "$REPO" --limit 1000 --json tagName -q '.[].tagName' |
  sort -V |
  while read -r tag; do
    [[ -n "$tag" ]] && echo "# delete_release \"$tag\""
  done

# Tags — commented out
echo
echo "# All Git tags (uncomment to delete)"
gh api "repos/$REPO/tags?per_page=100" --paginate --jq '.[].name' |
  sort -V |
  while read -r tag; do
    [[ -n "$tag" ]] && echo "# delete_tag \"$tag\""
  done

cat <<'EOF'

echo
EOF

