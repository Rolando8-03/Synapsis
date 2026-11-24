"""Compara la portada inmóvil y comprueba que el cambio de modo repone el desplazamiento."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication

from plataformas.escritorio import Handler, ROOT


EXERCISE = """
(async () => {
  const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
  const capture=async name=>{ document.title='PORTADA '+name; await wait(900); };
  await document.fonts.ready;
  await wait(1100);
  const mode=document.querySelector('#mode');
  const page=document.documentElement;
  if (!page.classList.contains('still')) throw Error('movimiento activo');
  scrollTo({top:0,behavior:'instant'});
  await capture('inicio');
  scrollTo({top:350,behavior:'instant'});
  await wait(150);
  const position=scrollY;
  if (position < 300) throw Error('no hubo desplazamiento de la portada');
  const area=()=>Array.from(document.querySelectorAll('#portada,.hero,.scene,#modulos'),
    element=>[element.getBoundingClientRect().top,element.getBoundingClientRect().height]);
  const before=area();
  mode.click();
  await wait(400);
  if (!page.classList.contains('serious') || location.hash!=='#modulos') throw Error('menú serio no abrió');
  await capture('seria');
  mode.click();
  await wait(400);
  if (page.classList.contains('serious') || location.hash!=='#portada' || Math.abs(scrollY-position)>1) {
    throw Error('Se perdió el desplazamiento al volver: '+[position,scrollY,location.hash]);
  }
  if (area().some((rect,i)=>rect.some((v,j)=>Math.abs(v-before[i][j])>1))) {
    throw Error('la geometría al volver difiere de la escena desplazada');
  }
  document.title='PORTADA FIN';
})().catch(error=>document.title='PORTADA ERROR '+error.message);
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="Directorio dist de la versión de partida.")
    parser.add_argument("--ancho", type=int, default=1366)
    options = parser.parse_args()
    app = QApplication([])
    views = []
    shots = [{}, {}]
    ended = set()
    sessions = []
    tasks = [("base", options.base.resolve()), ("actual", ROOT / "dist")]

    def record(title, i, view):
        if title == "PORTADA FIN":
            ended.add(i)
            if len(ended) == 2:
                app.exit(0)
        elif title.startswith("PORTADA ERROR"):
            print(title)
            app.exit(1)
        elif title.startswith("PORTADA "):
            label = title.removeprefix("PORTADA ")
            QTimer.singleShot(350, lambda: shots[i].update({label:view.grab().toImage()}))

    try:
        for i, (_, assets) in enumerate(tasks):
            server = ThreadingHTTPServer(("127.0.0.1", 0),partial(Handler, directory=str(assets)))
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            sessions.append((server, worker))
            view = QWebEngineView()
            profile = QWebEngineProfile(view)
            page = QWebEnginePage(profile, view)
            view.setPage(page)
            boot = QWebEngineScript()
            boot.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            boot.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            boot.setSourceCode("localStorage.setItem('synapsis-motion','true'); localStorage.setItem('synapsis-tema','dark');")
            page.scripts().insert(boot)
            view.resize(options.ancho,900)
            view.show()
            view.titleChanged.connect(partial(record,i=i,view=view))
            view.loadFinished.connect(lambda ok,page=page: page.runJavaScript(EXERCISE) if ok else app.exit(2))
            view.load(QUrl(f"http://127.0.0.1:{server.server_port}/#portada"))
            views.append(view)
        QTimer.singleShot(20000,lambda:app.exit(3))
        code = app.exec()
    finally:
        for server,worker in sessions:
            server.shutdown()
            worker.join()
            server.server_close()
    if code:
        return code
    names = ("inicio","seria")
    for name in names:
        first, second = (result.get(name) for result in shots)
        if first is None or second is None or first.isNull() or first != second:
            raise SystemExit("La captura difiere: "+name)
    print(f"{options.ancho}×900: {len(names)} capturas coincidentes con la base. Regreso al mismo desplazamiento.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
