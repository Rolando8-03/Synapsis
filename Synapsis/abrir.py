"""Ejecuta el servicio matemático local y abre la ventana de Synapsis."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import errno
import json
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit
import webbrowser

from backend import calculate, catalog
from nexolineal.domain.models import DomainError, InputError, ResourceLimitError

ROOT = Path(__file__).resolve().parent
MAX_BODY = 131_072
LOCAL_PORT = 47836

class Handler(SimpleHTTPRequestHandler):
    def address(self):
        return f"127.0.0.1:{self.server.server_port}"

    def send_json(self, body, status=200):
        data = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.headers.get("Host") != self.address():
            self.send_error(403)
        elif self.path == "/api/catalogo":
            self.send_json(catalog())
        elif self.path.startswith("/api/"):
            self.send_error(404)
        else:
            super().do_GET()

    def do_POST(self):
        if self.headers.get("Host") != self.address():
            self.send_error(403)
            return
        if self.path not in {"/api/calcular", "/api/kepler"}:
            self.send_error(404)
            return
        if (self.headers.get("Origin") not in (None, f"http://{self.address()}")
                or self.headers.get_content_type() != "application/json"):
            self.send_error(403)
            return
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= MAX_BODY:
                raise ValueError("La solicitud está vacía o excede el tamaño admitido.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Solicitud no válida.")
            if self.path == "/api/kepler":
                from kepler import orbital_frames
                self.send_json(orbital_frames(int(data["ley"]), float(data["forma"])))
            else:
                self.send_json(calculate(data.get("operation"), data.get("input"), data.get("steps") is not False))
        except (ValueError, KeyError, TypeError, ArithmeticError, DomainError, InputError, ResourceLimitError) as error:
            self.send_json({"status": "invalid_input", "error": {"message": str(error) or "Revisá los datos de entrada."}}, 400)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def list_directory(self, path):
        self.send_error(403)
        return None

    def log_message(self, *_):
        pass


def desktop(url):
    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication, QMainWindow
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
    except ImportError as error:
        raise SystemExit("Falta PySide6. En Windows ejecutá Abrir-Synapsis.cmd para instalarlo.") from error

    class LocalPage(QWebEnginePage):
        def acceptNavigationRequest(self, destination, kind, main_frame):
            return not main_frame or destination.host() == "127.0.0.1" and destination.port() == urlsplit(url).port

    app = QApplication([])
    app.setApplicationName("Synapsis")
    app.setWindowIcon(QIcon(str(ROOT / "dist" / "assets" / "favicon.svg")))
    window = QMainWindow()
    window.setWindowTitle("Synapsis · Observatorio matemático")
    window.resize(1380, 900)
    window.setMinimumSize(700, 560)
    view = QWebEngineView(window)
    profile = QWebEngineProfile("Synapsis", window)
    page = LocalPage(profile, view)
    page.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
    view.setPage(page)
    window.setCentralWidget(view)
    view.load(QUrl(url))
    window.show()
    code = app.exec()
    view.setPage(None)
    return code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Usar el navegador del sistema.")
    parser.add_argument("--sin-abrir", action="store_true", help="Servir los recursos sin abrir una ventana.")
    parser.add_argument("--puerto", type=int, help="Puerto local opcional.")
    flags = parser.parse_args()
    handler = partial(Handler, directory=str(ROOT / "dist"))
    try:
        service = ThreadingHTTPServer(("127.0.0.1", flags.puerto if flags.puerto is not None else LOCAL_PORT), handler)
    except OSError as error:
        if flags.puerto is not None or (error.errno not in (errno.EADDRINUSE, errno.EACCES) and getattr(error, "winerror", None) not in (10048, 10013)):
            raise
        service = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    with service as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        print(f"Synapsis: {url}", flush=True)
        if flags.sin_abrir or flags.web:
            if not flags.sin_abrir:
                Thread(target=webbrowser.open, args=(url,), daemon=True).start()
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            return 0
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            return desktop(url)
        finally:
            server.shutdown()
            worker.join()


if __name__ == "__main__":
    raise SystemExit(main())
