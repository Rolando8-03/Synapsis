"""Abre la ventana real con dependencias instaladas y comprueba que cierra el puerto."""
import json
from pathlib import Path
import platform
import socket
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import urlsplit

from PySide6.QtCore import QTimer, qVersion
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6 import QtWebEngineCore, QtWebEngineWidgets
from PySide6.QtWidgets import QApplication, QFileDialog

from importlib import import_module


EXERCISE = r"""
(async () => {
  const filled = async (fn, message) => {
    for (let i=0; i<300; i++) {
      const value=fn();
      if (value) return value;
      await new Promise(resolve=>setTimeout(resolve,30));
    }
    throw Error(message);
  };
  location.hash='grafica/calculo.derivar';
  const editor=await filled(()=>document.querySelector('#ws-fields math-field'), 'No cargó MathLive');
  const read=window.fetch.bind(window);
  let answer;
  window.fetch=async (url,options)=>{
    const response=await read(url,options);
    if (url==='/api/calcular') answer=await response.clone().json();
    return response;
  };
  editor.focus();
  const insert = label => {
    const key=[...document.querySelectorAll('.ws-power-keys button')].find(button=>
      button.textContent===label || button.getAttribute('aria-label')===label);
    if (!key) throw Error('Falta la tecla ' + label);
    key.click();
  };
  insert('x'); insert('Exponente'); insert('3');
  document.querySelector('#ws-calculate').focus();
  await new Promise(resolve=>setTimeout(resolve,90));
  document.querySelector('#ws-calculate').click();
  await filled(()=>answer && !document.querySelector('#ws-results').hidden, 'No se mostró el resultado');
  if (answer.result?.expresion !== '3*x^2' || !answer.steps?.length) throw Error('Derivada o pasos incorrectos');
  if (!document.querySelector('#ws-result-content math')) throw Error('No cargó KaTeX local');
  location.hash='orbita';
  document.querySelector('#kepler-chart').scrollIntoView();
  await filled(()=>!document.querySelector('#kepler-clock')?.disabled, 'No arrancó el reloj de Kepler');
  const time=document.querySelector('#kepler-time');
  time.value=6.43;
  time.dispatchEvent(new Event('input',{bubbles:true}));
  document.querySelector('#kepler-export').click();
})().catch(error=>document.title='ARRANQUE ERROR '+error.message+' · '+(document.querySelector('#ws-message')?.textContent || location.hash))
"""


class LocalOnly(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl()
        if url.scheme() in ("http", "https") and url.host() != "127.0.0.1":
            info.block(True)


def main():
    messages = []
    ports = []
    webview = QtWebEngineWidgets.QWebEngineView

    class Page(QtWebEngineCore.QWebEnginePage):
        def javaScriptConsoleMessage(self, level, message, line, source):
            if level == self.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
                print(f"JavaScript: {message} ({source}:{line})",file=sys.stderr)

    class Probe(webview):
        def load(self, url):
            ports.append(urlsplit(url.toString()).port)
            self.local_only = LocalOnly(self)
            self.page().profile().setUrlRequestInterceptor(self.local_only)
            self.loadFinished.connect(self.loaded)
            self.titleChanged.connect(self.completed)
            self.pdfPrintingFinished.connect(self.check_pdf)
            QTimer.singleShot(35000, lambda: QApplication.instance().exit(3))
            return super().load(url)

        def loaded(self, ok):
            if ok:
                self.page().runJavaScript(EXERCISE)
            else:
                QApplication.instance().exit(2)

        def completed(self, title):
            if not title.startswith("ARRANQUE "):
                return
            window = self.window()
            if not window.isWindow() or not window.isVisible() or not window.windowTitle().startswith("Synapsis"):
                title = "ARRANQUE ERROR No se abrió la ventana de Synapsis"
            messages.append(title)
            QTimer.singleShot(0, window.close)

        def check_pdf(self, path, success):
            pdf = QPdfDocument(self)
            if not success or pdf.load(path) != QPdfDocument.Error.None_:
                self.completed("ARRANQUE ERROR No se guardó el PDF de Kepler")
                return
            try:
                content = "\n".join(pdf.getAllText(i).text() for i in range(pdf.pageCount()))
            finally:
                pdf.close()
            if "Laboratorio de Kepler" in content and ("6.43 años" in content or "6,43 años" in content):
                self.completed("ARRANQUE OK")
            else:
                self.completed("ARRANQUE ERROR El PDF no contiene el instante del laboratorio")

    with (TemporaryDirectory() as temp,
          patch.object(QFileDialog, "getSaveFileName", return_value=(str(Path(temp) / "Kepler.pdf"), "")),
          patch.object(QtWebEngineWidgets, "QWebEngineView", Probe),
          patch.object(QtWebEngineCore, "QWebEnginePage", Page),
          patch.object(sys, "argv", ["abrir.py", "--puerto", "0"])):
        exit_code = import_module("abrir").launch()
    if exit_code or messages != ["ARRANQUE OK"]:
        raise SystemExit(str(messages or exit_code))
    with socket.socket() as probe:
        probe.settimeout(1)
        if probe.connect_ex(("127.0.0.1", ports[0])) == 0:
            raise SystemExit("El puerto del servicio sigue abierto.")
    print(json.dumps({"estado":"ok","qt":qVersion(),"equipo":platform.platform(),
                      "derivada":"3*x^2","pdf_kepler":True,"puerto_cerrado":True},ensure_ascii=False))


if __name__ == "__main__":
    main()
