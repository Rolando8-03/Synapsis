"""Ejecuta la verificación de entrega en una ventana Qt con un perfil aislado."""
import argparse
from dataclasses import asdict
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import platform
from threading import Thread

from PySide6.QtCore import QTimer, QUrl, qVersion
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication

from abrir import Handler, ROOT
from .casos import CASES, ALGEBRA


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ancho", type=int, default=1366)
    parser.add_argument("--dist", type=Path, default=ROOT / "dist", help="Activos de la revisión que se compara.")
    parser.add_argument("--medir", action="store_true", help="Ejecutar solo el escenario cronometrado.")
    options = parser.parse_args()
    app = QApplication([])
    metrics = []
    with ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(options.dist.resolve()))) as server:
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        view = QWebEngineView()
        profile = QWebEngineProfile()
        page = QWebEnginePage(profile, view)
        view.setPage(page)
        view.resize(options.ancho, 900)
        view.show()
        data = {"cases": [asdict(case) for case in CASES], "algebra": len(ALGEBRA), "measure": options.medir}
        script = "globalThis.delivery = " + json.dumps(data) + ";\n" + Path(__file__).with_suffix(".js").read_text(encoding="utf-8")
        view.loadFinished.connect(lambda ok: page.runJavaScript(script) if ok else app.exit(2))

        def completed(title):
            if title.startswith("ENTREGA "):
                metrics.append(json.loads(title.removeprefix("ENTREGA ")))
                app.exit(0 if metrics[-1]["ok"] else 1)

        view.titleChanged.connect(completed)
        view.load(QUrl(f"http://127.0.0.1:{server.server_port}/#sistemas/sistemas.resolver"))
        QTimer.singleShot(180000, lambda: app.exit(3))
        code = app.exec()
        print(json.dumps({"equipo": platform.platform(), "qt": qVersion(), "ancho": options.ancho,
                          "resultado": metrics[-1] if metrics else None}, ensure_ascii=False))
        view.setPage(None)
        server.shutdown()
        worker.join()
        return code


if __name__ == "__main__":
    raise SystemExit(main())
