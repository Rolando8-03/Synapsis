"""Comprueba una ventana de Synapsis empaquetada o iniciada con pythonw."""
import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import socket
import subprocess
from time import monotonic, sleep
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

from websocket import create_connection

from plataformas.paridad import CASES, compare, reference
from pruebas.entrega.arranque import EXERCISE


def wait_for(predicate, message, timeout=75):
    end = monotonic() + timeout
    while monotonic() < end:
        value = predicate()
        if value:
            return value
        sleep(.2)
    raise RuntimeError(message)


def local_port():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


def page_target(port, process):
    if process.poll() is not None:
        raise RuntimeError(f'Synapsis terminó al iniciar con código {process.returncode}.')
    try:
        with urlopen(f'http://127.0.0.1:{port}/json/list', timeout=2) as reply:
            targets = json.load(reply)
    except (URLError, TimeoutError, OSError):
        return None
    return next((target for target in targets if target.get('type') == 'page'
                 and urlsplit(target.get('url', '')).hostname == '127.0.0.1'), None)


def close_window(pid):
    user32 = ctypes.windll.user32
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @callback_type
    def close_if_synapsis(hwnd, _):
        owner = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            title = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(hwnd, title, len(title))
            if title.value.startswith('Synapsis'):
                user32.PostMessageW(hwnd, 0x0010, 0, 0)
        return True

    user32.EnumWindows(close_if_synapsis, 0)


def evaluate(connection, expression, await_promise=False):
    connection.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {
        'expression': expression, 'awaitPromise': await_promise, 'returnByValue': True,
    }}))
    while True:
        reply = json.loads(connection.recv())
        if reply.get('id') == 1:
            break
    data = reply.get('result', {})
    if 'error' in reply or 'exceptionDetails' in data:
        raise RuntimeError(data.get('exceptionDetails', reply.get('error')))
    return data.get('result', {}).get('value')


def verify(executable, script=None):
    port = local_port()
    web_port = local_port()
    args = [str(executable)]
    if script:
        args.append(str(script))
    args.extend(('--puerto', str(web_port)))
    env = os.environ.copy()
    env['QTWEBENGINE_REMOTE_DEBUGGING'] = f'127.0.0.1:{port}'
    env['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --proxy-server=127.0.0.1:1'
    cwd = script.parent if script else executable.parent
    with subprocess.Popen(args, cwd=cwd, env=env) as process:
        try:
            target = wait_for(lambda: page_target(port, process), 'No se abrió la ventana Qt ni su motor local.')
            connection = create_connection(target['webSocketDebuggerUrl'], timeout=15, suppress_origin=True)
            try:
                wait_for(lambda: evaluate(connection, 'document.querySelector("#workspace") !== null'),
                         'No se cargó la interfaz local.')
                evaluate(connection, EXERCISE)
                title = wait_for(lambda: (title if (title := evaluate(connection, 'document.title')).startswith('ARRANQUE ') else None),
                                 'No terminó el ejercicio con MathLive y KaTeX.')
                if title != 'ARRANQUE OK':
                    raise RuntimeError(title)
                data = evaluate(connection, '''(async () => {
                  const {motor} = await import(new URL('./transport.js', location.href));
                  const names = {catalogo:'catalog', calcular:'calculate', kepler:'orbit', 'kepler/escena':'scene'};
                  return Promise.all(CASES.map(([name,body]) => motor[names[name]](body ?? undefined)));
                })()'''.replace('CASES', json.dumps(CASES)), await_promise=True)
                compare(reference(), data)
            finally:
                connection.close()
            close_window(process.pid)
            if process.wait(timeout=10) != 0:
                raise RuntimeError('Synapsis no se cerró correctamente.')
        finally:
            if process.poll() is None:
                process.terminate()
    with socket.socket() as probe:
        probe.settimeout(1)
        if probe.connect_ex(('127.0.0.1', web_port)) == 0:
            raise RuntimeError('La ventana dejó abierto el puerto local.')
    print(json.dumps({'ventana': 'Synapsis', 'derivada': '3*x^2', 'casos': len(CASES), 'puerto_cerrado': True}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ejecutable', type=Path)
    parser.add_argument('--script', type=Path)
    args = parser.parse_args()
    verify(args.ejecutable.resolve(strict=True), args.script.resolve(strict=True) if args.script else None)


if __name__ == '__main__':
    main()
