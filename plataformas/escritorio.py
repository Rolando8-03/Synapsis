"""Ejecuta el servicio matemático local y abre la ventana de Synapsis."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import errno
import json
import os
from pathlib import Path
import sys
from threading import Thread
from traceback import format_exception
from urllib.parse import urlsplit
import webbrowser


def motor_api():
    from motor_matematico.platforms import api
    return api


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PORT = 47836

class Handler(SimpleHTTPRequestHandler):
    # En Windows, la asociación del registro puede variar para módulos JavaScript.
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript",
                      ".mjs": "text/javascript", ".css": "text/css"}

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
            status, reply = motor_api().invoke("catalogo")
            self.send_json(reply, status)
        elif self.path.startswith("/api/"):
            self.send_error(404)
        else:
            super().do_GET()

    def do_POST(self):
        if self.headers.get("Host") != self.address():
            self.send_error(403)
            return
        api = motor_api()
        action = self.path.removeprefix("/api/")
        if not self.path.startswith("/api/") or action not in api.OPERATIONS or action == "catalogo":
            self.send_error(404)
            return
        if (self.headers.get("Origin") not in (None, f"http://{self.address()}")
                or self.headers.get_content_type() != "application/json"):
            self.send_error(403)
            return
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= api.MAX_BODY:
                raise ValueError("La solicitud está vacía o excede el tamaño admitido.")
            try:
                data = json.loads(self.rfile.read(size))
            except ValueError as error:
                self.send_json(api.bad_request(error), 400)
                return
            status, reply = api.invoke(action, data)
            self.send_json(reply, status)
        except ValueError as error:
            self.send_json(api.bad_request(error), 400)
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
        from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineScript, QWebEngineSettings
    except ImportError as error:
        raise RuntimeError("Falta PySide6. Instalá las dependencias de requirements.txt.") from error

    class LocalPage(QWebEnginePage):
        def acceptNavigationRequest(self, destination, kind, main_frame):
            return not main_frame or destination.host() == "127.0.0.1" and destination.port() == urlsplit(url).port

    app = QApplication([])
    app.setApplicationName("Synapsis")
    app.setWindowIcon(QIcon(str(ROOT / "dist" / "assets" / "favicon.svg")))
    window = QMainWindow()
    window.setWindowTitle("Synapsis")
    window.resize(1380, 900)
    window.setMinimumSize(700, 560)
    view = QWebEngineView(window)
    profile = QWebEngineProfile("Synapsis", window)
    page = LocalPage(profile, view)
    page.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
    print_context = QWebEngineScript()
    print_context.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
    print_context.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    print_context.setSourceCode("window.SynapsisDesktop = true;")
    page.scripts().insert(print_context)
    view.setPage(page)
    window.setCentralWidget(view)
    def save_report_pdf():
        path, _ = QFileDialog.getSaveFileName(window, "Guardar informe de Synapsis", "Synapsis.pdf",
                                               "Documento PDF (*.pdf)")
        if path:
            view.printToPdf(path if path.lower().endswith(".pdf") else path + ".pdf")
        else:
            page.runJavaScript("dispatchEvent(new Event('synapsis:print-finished'))")

    def report_finished(path, success):
        page.runJavaScript("dispatchEvent(new Event('synapsis:print-finished'))")
        if not success:
            QMessageBox.warning(window, "Synapsis", f"No se pudo guardar el informe en {path}.")

    def save_graph(download):
        if not download.url().toString().startswith("data:image/png;base64,"):
            return
        path, _ = QFileDialog.getSaveFileName(window, "Guardar gráfica", "synapsis-grafica.png",
                                               "Imagen PNG (*.png)")
        if path:
            target = Path(path if path.lower().endswith(".png") else path + ".png")
            download.setDownloadDirectory(str(target.parent))
            download.setDownloadFileName(target.name)
            download.accept()
        else:
            download.cancel()

    profile.downloadRequested.connect(save_graph)
    view.printRequested.connect(save_report_pdf)
    view.pdfPrintingFinished.connect(report_finished)
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
    motor_api()
    handler = partial(Handler, directory=str(ROOT / "dist"))
    try:
        service = ThreadingHTTPServer(("127.0.0.1", flags.puerto if flags.puerto is not None else LOCAL_PORT), handler)
    except OSError as error:
        if flags.puerto is not None or (error.errno not in (errno.EADDRINUSE, errno.EACCES) and getattr(error, "winerror", None) not in (10048, 10013)):
            raise
        service = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    with service as server:
        url = f"http://127.0.0.1:{server.server_port}/"
        if sys.stdout is not None:
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


def show_startup_error(error):
    message = "Synapsis no pudo arrancar. " + (str(error) or type(error).__name__)
    if sys.stderr is not None:
        print(message, file=sys.stderr)
    if log := os.environ.get("SYNAPSIS_INFORME_ARRANQUE"):
        try:
            Path(log).write_text("".join(format_exception(error)), encoding="utf-8")
        except OSError:
            pass
    if "--sin-abrir" in sys.argv or "--web" in sys.argv:
        return
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication([])
        QMessageBox.critical(None, "Synapsis", message)
    except (ImportError, RuntimeError):
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, "Synapsis", 0x10)


def launch():
    try:
        return main()
    except (OSError, ImportError, RuntimeError) as error:
        show_startup_error(error)
        return 1
