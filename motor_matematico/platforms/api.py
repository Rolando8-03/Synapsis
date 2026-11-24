"""Contrato JSON compartido por el servicio local y el trabajador WebAssembly."""
import json

from motor_matematico.application.backend import calculate, catalog
from motor_matematico.algorithms.kepler import orbital_frames, scene_frames
from motor_matematico.domain.models import DomainError, InputError, ResourceLimitError

MAX_BODY = 131_072
OPERATIONS = {
    "catalogo": lambda _: catalog(),
    "calcular": lambda d: calculate(d.get("operation"), d.get("input"), d.get("steps") is not False),
    "kepler": lambda d: orbital_frames(int(d["ley"]), float(d["forma"])),
    "kepler/escena": lambda d: scene_frames(float(d["excentricidad"]), float(d["semieje_b"]),
                                            float(d.get("excentricidad_b", .30))),
}
MATH_ERRORS = (ValueError, KeyError, TypeError, ArithmeticError, DomainError, InputError, ResourceLimitError)


def invoke(action, data=None):
    if action not in OPERATIONS:
        return 404, {"status": "invalid_input", "error": {"message": "Operación del motor desconocida."}}
    try:
        if data is None and action == "catalogo":
            data = {}
        if not isinstance(data, dict):
            raise ValueError("Solicitud no válida.")
        return 200, OPERATIONS[action](data)
    except MATH_ERRORS as error:
        return 400, bad_request(error)


def bad_request(error):
    return {"status": "invalid_input", "error": {"message": str(error) or "Revisá los datos de entrada."}}


def invoke_json(action, text):
    if len(text.encode()) > MAX_BODY:
        status, reply = 400, bad_request("La solicitud supera el tamaño admitido.")
    else:
        try:
            data = json.loads(text)
        except (ValueError, TypeError) as error:
            status, reply = 400, bad_request(error)
        else:
            status, reply = invoke(action, data)
    return json.dumps({"status":status, "data":reply}, ensure_ascii=False, allow_nan=False)
