"""Genera la distribución web hermética para Pages y Android."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from urllib.request import urlopen
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "dist" / "runtime"
SOURCE_PACKAGES = ("ampliaciones", "motor_grupo4", "motor_matematico")
CORE = ("pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "pyodide-lock.json", "python_stdlib.zip")


def sources():
    modules = sorted(path for path in ROOT.glob("*.py") if path.name != "abrir.py")
    modules += sorted(path for name in SOURCE_PACKAGES for path in (ROOT / name).rglob("*.py"))
    if any(path.is_symlink() for path in modules):
        raise ValueError("La distribución solo admite fuentes regulares.")
    return modules


def manifest():
    return json.dumps([p.relative_to(ROOT).as_posix() for p in sources()], indent=2) + "\n"


def download(url, target, expected=None):
    with urlopen(url, timeout=60) as response:
        data = response.read(64*1024*1024 + 1)
    if not data or len(data)>64*1024*1024:
        raise ValueError(f"Tamaño inesperado de {target.name}.")
    if expected and hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"La suma SHA-256 de {target.name} no coincide.")
    target.write_bytes(data)


def build(output):
    if output == ROOT or output in ROOT.parents or (ROOT / 'dist') in (output,*output.parents):
        raise ValueError("Elegí un directorio de salida separado de las fuentes.")
    if output.exists():
        raise ValueError("El directorio de salida ya existe. Elegí una carpeta nueva.")
    output.mkdir(parents=True)
    shutil.copyfile(ROOT / "index.html", output / "index.html")
    shutil.copytree(ROOT / "dist", output / "dist")
    (output / ".nojekyll").touch()
    metadata = {"version": (ROOT / "plataformas" / "VERSION").read_text().strip(),
                "revision": os.environ.get("GITHUB_SHA")}
    (output / "version-compilada.json").write_text(json.dumps(metadata) + "\n", encoding="utf-8")
    runtime = output / "dist" / "runtime"
    pyodide = runtime / "pyodide"
    pyodide.mkdir()
    versions = json.loads((RUNTIME / "version.json").read_text())
    url = f"https://cdn.jsdelivr.net/pyodide/v{versions['pyodide']}/full/"
    locked = json.loads((RUNTIME / "pyodide-sha256.json").read_text())
    for name in CORE:
        download(url + name, pyodide / name, locked[name])
    for wheel in versions["wheels"]:
        download(wheel["url"], runtime / wheel["file"], wheel["sha256"])
    with ZipFile(runtime / "python.zip", "w", ZIP_DEFLATED) as archive:
        for path in sources():
            archive.write(path, path.relative_to(ROOT).as_posix())
    (runtime / "empaquetado.json").write_text('{"local":true}\n', encoding="utf-8")
    total = sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
    print(f"Distribución web en {output} ({total} bytes).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--output", type=Path)
    args = parser.parse_args()
    path = RUNTIME / "archivos.json"
    if args.manifest:
        path.write_text(manifest(), encoding="utf-8", newline="\n")
    elif args.check:
        if path.read_text(encoding="utf-8") != manifest():
            parser.error("Actualizá el manifiesto con python -m plataformas.web --manifest.")
    else:
        build(args.output.resolve())


if __name__ == "__main__":
    main()
