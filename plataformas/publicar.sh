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
android=Synapsis-Android-debug.apk
signed_android=Synapsis-Android.apk

root=$PWD
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"

check_tag() {
  local ref peeled
  ref=$(git -C "$root" ls-remote origin "refs/tags/$tag" "refs/tags/$tag^{}")
  if [[ -n "$ref" ]]; then
    peeled=$(tail -n 1 <<< "$ref" | cut -f1)
    test "$peeled" = "$GITHUB_SHA"
  fi
}

download_public() {
  curl -q -fsSL --retry 4 --retry-all-errors --max-time 180 --output "$2" "$source_url/releases/$1"
}

render_notes() {
  cat <<NOTES
## Synapsis $version

Revisión: \`$GITHUB_SHA\`

- [GitHub Pages]($site)
- [GitHub Packages]($package_url) · \`$package\`
- [Pruebas de esta compilación]($source_url/actions/runs/$GITHUB_RUN_ID)

### Instalación y verificación

- Windows Server 2025 x64: instalación por usuario, acceso desde Inicio, cálculo local, reinstalación y desinstalación.
- Android: APK de prueba para instalación directa, con firma de depuración verificada. El APK de prueba tiene su propio identificador de aplicación.
NOTES
  if [[ -f "assets/$signed_android" ]]; then
    printf '%s\n' '- APK de distribución: firma estable, instalación y arranque sin conexión verificados en el emulador Android API 35.'
  fi
  printf '\n### SHA-256\n\n'
  printf '```text\n'
  cat SHA256SUMS
  printf '```\n'
}

publish_release() {
  local revision= file source
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
  check_tag

  if ! gh release view "$tag" --repo "$GITHUB_REPOSITORY" --json targetCommitish,isDraft,assets > release.json; then
    gh release create "$tag" --repo "$GITHUB_REPOSITORY" --target "$GITHUB_SHA" --draft \
      --title "Synapsis $version" --notes "Compilación desde $GITHUB_SHA."
    gh release view "$tag" --repo "$GITHUB_REPOSITORY" --json targetCommitish,isDraft,assets > release.json
  fi
  jq -e --arg sha "$GITHUB_SHA" '.targetCommitish == $sha' release.json >/dev/null

  files=("$windows" "$android")
  if [[ -f "$root/build/android/$signed_android" ]] ||
    jq -e --arg name "$signed_android" 'any(.assets[]; .name == $name)' release.json >/dev/null; then
    files+=("$signed_android")
  fi
  mkdir assets received public
  for file in "${files[@]}"; do
    if jq -e --arg name "$file" 'any(.assets[]; .name == $name)' release.json >/dev/null; then
      gh release download "$tag" --pattern "$file" --dir assets --repo "$GITHUB_REPOSITORY"
    else
      source="$root/build/android/$file"
      [[ "$file" != "$windows" ]] || source="$root/build/windows/$file"
      cp "$source" "assets/$file"
      gh release upload "$tag" "assets/$file" --repo "$GITHUB_REPOSITORY"
    fi
    gh release download "$tag" --pattern "$file" --dir received --repo "$GITHUB_REPOSITORY"
  done
  test "$(head -c 2 "assets/$windows")" = MZ
  test "$(head -c 2 "assets/$android")" = PK
  (cd assets && sha256sum "${files[@]}") > SHA256SUMS
  (cd received && sha256sum -c ../SHA256SUMS)
  render_notes > notes.md
  gh release edit "$tag" --repo "$GITHUB_REPOSITORY" --draft=false --latest --notes-file notes.md

  for file in "${files[@]}"; do
    download_public "latest/download/$file" "public/$file"
  done
  (cd public && sha256sum -c ../SHA256SUMS)
  printf '[Descargas de Synapsis %s](%s/releases/tag/%s)\n' "$version" "$source_url" "$tag" >> "$GITHUB_STEP_SUMMARY"
}

publish_package() {
  local file digest
  check_tag
  for file in "$windows" "$android"; do
    download_public "download/$tag/$file" "$file"
    digest=$(gh api "repos/$GITHUB_REPOSITORY/releases/tags/$tag" \
      --jq ".assets[] | select(.name == \"$file\") | .digest")
    [[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]]
    printf '%s  %s\n' "${digest#sha256:}" "$file" | sha256sum -c
  done
  sha256sum "$windows" "$android" > SHA256SUMS
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
      "$android:application/vnd.synapsis.android.debug.v1"
    oras manifest fetch --registry-config auth.json "$package" > manifest.json
  fi
  jq -e --arg sha "$GITHUB_SHA" --arg source "$source_url" --arg version "$version" '
    .annotations["org.opencontainers.image.revision"] == $sha and
    .annotations["org.opencontainers.image.source"] == $source and
    .annotations["org.opencontainers.image.version"] == $version and
    (.layers | length) == 2
  ' manifest.json >/dev/null
  oras pull --registry-config auth.json --output package "$package"
  (cd package && sha256sum -c ../SHA256SUMS)
  if oras pull --registry-config anon.json --output public-package "$package"; then
    (cd public-package && sha256sum -c ../SHA256SUMS)
    printf '[Paquete público de Synapsis %s](%s)\n' "$version" "$package_url" >> "$GITHUB_STEP_SUMMARY"
  else
    echo "::warning::El paquete está publicado y sus archivos se verificaron con acceso. La descarga anónima queda pendiente de visibilidad en $package_url."
    printf '[Paquete de Synapsis %s](%s) pendiente de acceso público.\n' "$version" "$package_url" >> "$GITHUB_STEP_SUMMARY"
  fi
}

case "${1:-}" in
  release) publish_release ;;
  paquete) publish_package ;;
  *) echo 'Uso: publicar.sh release|paquete' >&2; exit 2 ;;
esac
