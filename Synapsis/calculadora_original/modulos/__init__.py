"""Inicializa el paquete de módulos de NexoLineal.
Organiza los componentes de la calculadora de Álgebra Lineal.
Autores: Grupo 4 de Álgebra Lineal.
"""

import sys
from pathlib import Path


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent


CARPETA_PYTHON = CARPETA_PROYECTO / "python"


if str(CARPETA_PYTHON) not in sys.path:
    sys.path.insert(0, str(CARPETA_PYTHON))

    