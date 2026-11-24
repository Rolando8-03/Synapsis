"""Abre la web y comprueba el trabajador, la interfaz y la paridad con Python local."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from threading import Thread
from urllib.parse import urlsplit

from PySide6.QtCore import QTimer, QUrl, qVersion
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineUrlRequestInterceptor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication

from .paridad import CASES, compare, reference


class StaticHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/Synapsis/'):
            self.path = self.path.removeprefix('/Synapsis')
        if not self.path.startswith('/api/'):
            super().do_GET()
        else:
            self.send_error(501, 'Solo archivos estáticos')

    def log_message(self, format, *args):
        if args[1] not in ('200', '304', '404'):
            super().log_message(format, *args)


class Network(QWebEngineUrlRequestInterceptor):
    def __init__(self, hosts, parent):
        super().__init__(parent)
        self.hosts = hosts

    def interceptRequest(self, info):
        url = info.requestUrl()
        if url.scheme() in ('http', 'https') and url.host() not in self.hosts:
            info.block(True)


class Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        if level == self.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            print(f'{source}:{line}: {message}', file=sys.stderr)


def verify(url, cdn):
    app = QApplication([])
    view = QWebEngineView()
    page = Page(view)
    view.setPage(page)
    hosts = {urlsplit(url).hostname}
    if cdn:
        hosts.update(('cdn.jsdelivr.net', 'files.pythonhosted.org'))
    network = Network(hosts, view)
    page.profile().setUrlRequestInterceptor(network)
    view.resize(1120, 850)
    view.show()
    script = (Path(__file__).with_name('verificar_web.js').read_text(encoding='utf-8')
              .replace('__CASOS__', json.dumps(CASES)))
    finished = False

    def loaded(ok):
        nonlocal finished
        if not ok:
            app.exit(2)
        elif not finished and view.url().path().endswith('/dist/index.html'):
            finished = True
            page.runJavaScript(script)

    def report(title):
        if title.startswith('PARIDAD ERROR '):
            print(title, file=sys.stderr)
            app.exit(1)
        if title == 'PARIDAD OK':
            page.runJavaScript('JSON.stringify(window.synapsisParity)', compare_report)

    def compare_report(value):
        try:
            result = json.loads(value)
            compare(reference(), result.pop('answers'))
        except (AssertionError, TypeError, ValueError) as error:
            print(error, file=sys.stderr)
            app.exit(1)
        else:
            print(json.dumps({'qt': qVersion(), 'url': url, **result}, ensure_ascii=False), flush=True)
            app.exit(0)

    view.loadFinished.connect(loaded)
    view.titleChanged.connect(report)
    QTimer.singleShot(170_000, lambda: app.exit(3))
    view.load(QUrl(url))
    code = app.exec()
    page.profile().setUrlRequestInterceptor(None)
    view.close()
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--directorio', type=Path)
    group.add_argument('--url')
    parser.add_argument('--prefijo', action='store_true')
    parser.add_argument('--cdn', action='store_true', help='Permite la primera carga desde un clon limpio.')
    args = parser.parse_args()
    if args.url:
        return verify(args.url, args.cdn)
    with ThreadingHTTPServer(('127.0.0.1', 0), partial(StaticHandler, directory=args.directorio)) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        relative = 'Synapsis/' if args.prefijo else ''
        try:
            return verify(f'http://127.0.0.1:{server.server_port}/{relative}index.html', args.cdn)
        finally:
            server.shutdown()


if __name__ == '__main__':
    sys.exit(main())
