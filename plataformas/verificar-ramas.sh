#!/usr/bin/env bash
set -euo pipefail

# Se invoca solo después de comprobar las descargas públicas de la entrega.
git fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune
gh pr list --repo "$GITHUB_REPOSITORY" --state all --limit 200 \
  --json number,state,headRefName,baseRefName,mergedAt --jq '.[] | [.number,.state,.headRefName,.baseRefName,.mergedAt] | @tsv'
mapfile -t heads < <(git ls-remote --heads origin)
leases=()
deletions=()
main=
for head in "${heads[@]}"; do
  read -r sha ref <<< "$head"
  if [[ "$ref" == refs/heads/main ]]; then
    main="$sha"
    continue
  fi
  git cat-file -e "$sha^{commit}"
  printf '%s %s · commits exclusivos de main y de la rama, comparados por parche\n' "$ref" "$sha"
  git rev-list --left-right --cherry-pick --count "$GITHUB_SHA...$sha"
  git diff --shortstat "$GITHUB_SHA...$sha"
  leases+=("--force-with-lease=$ref:$sha")
  deletions+=(":$ref")
done
test "$main" = "$GITHUB_SHA"
if (( ${#deletions[@]} )); then
  git push --atomic "${leases[@]}" origin "${deletions[@]}"
fi
result=$(git ls-remote --heads origin)
printf '%s\n' "$result" | tee -a "$GITHUB_STEP_SUMMARY"
test "$result" = "$(printf '%s\trefs/heads/main' "$GITHUB_SHA")"
