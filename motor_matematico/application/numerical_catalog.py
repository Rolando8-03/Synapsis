"""Formularios de métodos numéricos: datos mínimos y opciones visibles editables."""


def field(
    name,
    label,
    kind="scalar",
    default="",
    required=False,
    choices=None,
    when=None,
    required_when=None,
):
    result = dict(name=name, label=label, kind=kind, default=default, required=required)
    if choices:
        result["choices"] = choices
    if when:
        result["when"] = when
    if required_when:
        result["required_when"] = required_when
    return result


def spec(id, title, fields, description, category="Métodos numéricos"):
    return dict(
        id=id, title=title, category=category, fields=fields, description=description
    )


EXPRESSION = field("expresion", "Función f(x)", "expression", "x^2-2", True)
TOLS = [
    field("tolerancia_x", "Tolerancia en x · fracción si el criterio es relativo", default="1e-8"),
    field("tolerancia_f", "Tolerancia absoluta del residual", default="1e-8"),
    field("max_iteraciones", "Máximo de iteraciones", "integer", "100"),
]
NUMERICAL_DATA = [
    spec(
        "funciones.evaluar",
        "Evaluar una función y su dominio",
        [
            EXPRESSION,
            field("punto", "Punto de evaluación", default="1", required=True),
            field("inferior", "Extremo inferior del intervalo opcional"),
            field("superior", "Extremo superior del intervalo opcional"),
        ],
        "Lenguaje seguro: números, x, operadores y funciones admitidas. Ans no se admite como variable de función.",
    )
]
for method, title in [
    ("biseccion", "Bisección"),
    ("falsa_posicion", "Falsa posición"),
    ("newton", "Newton"),
    ("secante", "Secante"),
]:
    seeds = (
        [
            field("inferior", "Extremo inferior", default="1", required=True),
            field("superior", "Extremo superior", default="2", required=True),
        ]
        if method in ("biseccion", "falsa_posicion")
        else (
            [field("anterior", "Primera semilla", default="1", required=True)]
            if method == "secante"
            else []
        )
        + [
            field(
                "inicial",
                "Semilla inicial" if method == "newton" else "Segunda semilla",
                default="1.5",
                required=True,
            )
        ]
    )
    options = (
        [field("derivada", "Derivada f′(x), vacía usa reglas simbólicas", "expression"),
         field("multiplicidad","Multiplicidad conocida · 1 para Newton estándar","integer","1")]
        if method == "newton"
        else []
    )
    choices = (
        ["cota", "residual", "ambos", "relativo"]
        if method == "biseccion"
        else ["residual_y_paso", "relativo_y_residual", "residual"] if method == "newton" else ["residual_y_paso", "residual"]
    )
    NUMERICAL_DATA.append(
        spec(
            "raices." + method,
            title,
            [
                EXPRESSION,
                *seeds,
                *options,
                *TOLS,
                field(
                    "criterio",
                    "Criterio de parada",
                    "select",
                    choices[0],
                    choices=choices,
                ),
            ],
            "El residual y el cambio entre iterados son medidas distintas. Solo se declara una cota garantizada cuando el motor puede justificarla.",
        )
    )
for method, title in [("jacobi", "Jacobi"), ("gauss_seidel", "Gauss-Seidel"), ("sor", "Relajación SOR")]:
    NUMERICAL_DATA.append(
        spec(
            "iterativos." + method,
            title,
            [
                field("A", "Matriz de coeficientes A", "matrix", "4 1\n2 3", True),
                field("b", "Vector b", "vector", "1 2", True),
                field("inicial", "Vector inicial, vacío usa ceros", "vector"),
                *([field("omega", "Factor de relajación ω · entre 0 y 2", default="1.2", required=True)] if method == "sor" else []),
                field("criterio", "Criterio de parada", "select", "paso_y_residual",
                      choices=["paso_y_residual", "paso_absoluto", "relativo_vectorial", "porcentaje_por_componente", "solo_residual"]),
                field(
                    "norma",
                    "Norma para el criterio",
                    "select",
                    "infinito",
                    choices=["infinito", "uno", "dos"],
                ),
                field("tolerancia_absoluta", "Tolerancia absoluta", default="1e-8"),
                field("tolerancia_relativa", "Tolerancia relativa", default="1e-8"),
                field("max_iteraciones", "Máximo de iteraciones", "integer", "100"),
                field("referencia", "Solución de referencia, opcional", "vector"),
            ],
            "La dimensión se infiere de A. Elegí el criterio de parada y sus unidades. La tabla muestra el residual y los cambios entre iteraciones.",
        )
    )
NUMERICAL_DATA.extend(
    [
        spec(
            "errores.calcular",
            "Errores absoluto, relativo y porcentual",
            [
                field("aproximado", "Valor aproximado", default="22/7", required=True),
                field("referencia", "Valor de referencia", default="3.1416"),
                field("anterior", "Aproximación anterior"),
            ],
            "El error respecto a la referencia y el cambio aproximado se informan por separado. Relativo y porcentual no se definen si su denominador es cero.",
            "Herramientas",
        ),
        spec(
            "conversiones.bases",
            "Conversión de bases 2, 8, 10 y 16",
            [
                field(
                    "numero",
                    "Numeral, admite períodos como 0.(3)",
                    "text",
                    "10.625",
                    True,
                ),
                field(
                    "base_origen",
                    "Base de origen",
                    "select",
                    "10",
                    choices=["2", "8", "10", "16"],
                ),
                field(
                    "base_destino",
                    "Base de destino",
                    "select",
                    "2",
                    choices=["2", "8", "10", "16"],
                ),
                field("precision", "Máximo de dígitos fraccionarios", "integer", "16"),
            ],
            "Conversión racional exacta o truncamiento declarado; incluye desarrollo posicional y comprobación inversa.",
            "Herramientas",
        ),
        spec(
            "conjuntos.operar",
            "Conjuntos finitos",
            [
                field(
                    "operacion",
                    "Operación",
                    "select",
                    "union",
                    choices=[
                        "union",
                        "interseccion",
                        "diferencia",
                        "diferencia_simetrica",
                        "complemento",
                        "producto_cartesiano",
                    ],
                ),
                field("A", "Conjunto A: una etiqueta por línea", "set", "a\nb", True),
                field(
                    "B",
                    "Conjunto B",
                    "set",
                    "b\nc",
                    when={
                        "operacion": [
                            "union",
                            "interseccion",
                            "diferencia",
                            "diferencia_simetrica",
                            "producto_cartesiano",
                        ]
                    },
                ),
                field(
                    "universo",
                    "Universo U",
                    "set",
                    "",
                    when={"operacion": ["complemento"]},
                    required_when={"operacion": ["complemento"]},
                ),
            ],
            "Las etiquetas son texto, sin duplicados; [] representa vacío. El complemento requiere universo explícito.",
            "Herramientas",
        ),
        spec(
            "calculo.primitiva",
            "Primitiva de reglas admitidas",
            [
                field("expresion", "Integrando", "expression", "x^2", True),
                field("variable", "Variable de integración", "select", "x", choices=["x"]),
            ],
            "Polinomios de grado hasta 30, sumas y múltiplos constantes, sin/cos/exp de argumento afín y 1/x. Se añade la constante C.",
            "Herramientas",
        ),
        spec(
            "calculo.numerica",
            "Integral numérica con precisión editable",
            [
                field("expresion", "Función f(x)", "expression", "x^4", True),
                field("inferior", "Límite inferior", default="0", required=True),
                field("superior", "Límite superior", default="1", required=True),
                field("tolerancia", "Tolerancia absoluta", default="1e-8"),
                field(
                    "max_subintervalos",
                    "Máximo de subintervalos (potencia de dos)",
                    "integer",
                    "1024",
                ),
            ],
            "Simpson compuesto con refinamiento. Cota garantizada para polinomios racionales; estimación no garantizada para otras funciones.",
            "Herramientas",
        ),
    ]
)
NUMERICAL_IDS = {item["id"] for item in NUMERICAL_DATA}
