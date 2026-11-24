#!/usr/bin/env bash
set -euo pipefail

test "$GITHUB_REF" = refs/heads/main
test "$(git rev-parse HEAD)" = "$GITHUB_SHA"
version=$(cat plataformas/VERSION)
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
tag="v$version"
source_url="https://github.com/$GITHUB_REPOSITORY"
site="https://${GITHUB_REPOSITORY_OWNER,,}.github.io/${GITHUB_REPOSITORY#*/}/"
package="ghcr.io/${GITHUB_REPOSITORY,,}:$version"
package_url="$source_url/pkgs/container/$(basename "${GITHUB_REPOSITORY,,}")"
windows=Synapsis-Setup.exe
android=Synapsis-Android.apk
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

revision=
for attempt in {1..24}; do
  revision=$(curl -fsSL --max-time 12 -H 'Cache-Control: no-cache' \
    "${site}version-compilada.json?sha=$GITHUB_SHA" | jq -er .revision) || true
  [[ "$revision" == "$GITHUB_SHA" ]] && break
  sleep 10
done
if [[ "$revision" != "$GITHUB_SHA" ]]; then
  echo "::error::Pages debe publicar $GITHUB_SHA antes de crear esta entrega."
  exit 1
fi

cp "build/windows/$windows" "build/android/$android" "$work/"
cd "$work"
test "$(head -c 2 "$windows")" = MZ
test "$(head -c 2 "$android")" = PK
printf '{"auths":{}}\n' > anon.json
printf '%s' "$GH_TOKEN" | oras login ghcr.io --username "$GITHUB_ACTOR" --password-stdin --registry-config auth.json
if ! oras manifest fetch --registry-config auth.json "$package" > manifest.json 2> registry-error.txt; then
  if ! grep -Eqi 'manifest unknown|not found|404|denied|forbidden' registry-error.txt; then
    cat registry-error.txt >&2
    exit 1
  fi
  oras push --registry-config auth.json \
    --artifact-type application/vnd.synapsis.distribution.v1 \
    --annotation "org.opencontainers.image.source=$source_url" \
    --annotation "org.opencontainers.image.version=$version" \
    --annotation "org.opencontainers.image.revision=$GITHUB_SHA" \
    "$package" \
    "$windows:application/vnd.synapsis.windows-x64.installer.v1" \
    "$android:application/vnd.synapsis.android.installer.v1"
fi
if ! oras manifest fetch --registry-config anon.json "$package" > manifest.json; then
  echo "::error::Hacé público el paquete Synapsis en $package_url y reintentá esta ejecución."
  exit 1
fi

jq -e --arg sha "$GITHUB_SHA" --arg source "$source_url" --arg version "$version" \
  --arg windows "$windows" --arg android "$android" '
  .annotations["org.opencontainers.image.revision"] == $sha and
  .annotations["org.opencontainers.image.source"] == $source and
  .annotations["org.opencontainers.image.version"] == $version and
  (.layers | length) == 2 and
  any(.layers[]; .annotations["org.opencontainers.image.title"] == $windows and
                 .mediaType == "application/vnd.synapsis.windows-x64.installer.v1") and
  any(.layers[]; .annotations["org.opencontainers.image.title"] == $android and
                 .mediaType == "application/vnd.synapsis.android.installer.v1")
' manifest.json >/dev/null
oras pull --registry-config anon.json --output package "$package"
for file in "$windows" "$android"; do
  expected=$(jq -er --arg file "$file" '.layers[] | select(.annotations["org.opencontainers.image.title"] == $file) | .digest | sub("^sha256:";"")' manifest.json)
  printf '%s  package/%s\n' "$expected" "$file" | sha256sum -c
done
test "$(head -c 2 "package/$windows")" = MZ
test "$(head -c 2 "package/$android")" = PK
(cd package && sha256sum "$windows" "$android") > SHA256SUMS

# Impide reutilizar una etiqueta con contenido de otra revisión.
refs=$(git -C "$GITHUB_WORKSPACE" ls-remote origin "refs/tags/$tag" "refs/tags/$tag^{}")
if [[ -n "$refs" ]]; then
  sha=$(tail -n 1 <<< "$refs" | cut -f1)
  test "$sha" = "$GITHUB_SHA"
fi
if gh release view "$tag" --repo "$GITHUB_REPOSITORY" --json targetCommitish,isDraft,assets > release.json; then
  jq -e --arg sha "$GITHUB_SHA" '.targetCommitish == $sha' release.json >/dev/null
else
  cat > notes.md <<NOTES
## Synapsis $version

Revisión: \`$GITHUB_SHA\`

- [GitHub Pages]($site)
- [GitHub Packages]($package_url) · \`$package\`
- [Pruebas de esta compilación]($source_url/actions/runs/$GITHUB_RUN_ID)

### Instalación comprobada

- Windows Server 2025 x64: instalación por usuario, acceso desde Inicio, cálculo local, reinstalación y desinstalación.
- Emulador Android API 35 x86_64: firma de distribución verificada, instalación y apertura de Synapsis sin conexión.

### SHA-256

\`\`\`text
$(cat SHA256SUMS)
\`\`\`
NOTES
  gh release create "$tag" --repo "$GITHUB_REPOSITORY" --target "$GITHUB_SHA" --draft \
    --title "Synapsis $version" --notes-file notes.md
  gh release view "$tag" --repo "$GITHUB_REPOSITORY" --json targetCommitish,isDraft,assets > release.json
fi
mkdir release
for file in "$windows" "$android"; do
  if ! jq -e --arg file "$file" 'any(.assets[]; .name == $file)' release.json >/dev/null; then
    gh release upload "$tag" "package/$file" --repo "$GITHUB_REPOSITORY"
  fi
  gh release download "$tag" --pattern "$file" --dir release --repo "$GITHUB_REPOSITORY"
done
(cd release && sha256sum -c ../SHA256SUMS)
if jq -e .isDraft release.json >/dev/null; then
  gh release edit "$tag" --repo "$GITHUB_REPOSITORY" --draft=false --latest
fi

# curl no usa credenciales de gh ni de ORAS.
mkdir public
for file in "$windows" "$android"; do
  curl -q -fsSL --retry 5 --retry-all-errors --max-time 180 --output "public/$file" \
    "$source_url/releases/latest/download/$file"
done
(cd public && sha256sum -c ../SHA256SUMS)
{
  printf '[Release](%s/releases/tag/%s) · [Paquete](%s)\n\n' "$source_url" "$tag" "$package_url"
  printf '```text\n'
  cat SHA256SUMS
  printf '```\n'
} >> "$GITHUB_STEP_SUMMARY"
