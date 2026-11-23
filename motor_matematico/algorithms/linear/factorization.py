"""LU docente sin intercambios y PLU rectangular con PA=LU."""

from fractions import Fraction as F
from .context import (
    Context,
    identity,
    matrix,
    multiply,
    matvec,
    freeze,
    LinearFailure,
    InputError,
    tex,
)
from .reduction import solve
from .worked import dot_formula, product_steps, row_replacement


def factor(A, ctx, pivoting=False, b=None):
    m, n = len(A), len(A[0])
    U = [row[:] for row in A]
    L, P = identity(m), identity(m)
    row = 0
    pivots = []
    ctx.emit("factorizacion_inicial", "Iniciar U=A y L=P=I.", {"U": U, "L": L, "P": P})
    for col in range(n):
        if row == m:
            break
        available = [i for i in range(row, m) if U[i][col]]
        if not available:
            continue
        chosen = max(available, key=lambda i: abs(U[i][col])) if pivoting else row
        if not pivoting and not U[row][col]:
            raise LinearFailure(
                "not_applicable",
                "LU sin permutación requiere un intercambio. Elegí PLU.",
                {"fila": row, "columna": col},
            )
        if chosen != row:
            old_multipliers = [L[row][:row], L[chosen][:row]]
            U[row], U[chosen] = U[chosen], U[row]
            P[row], P[chosen] = P[chosen], P[row]
            # Solo se permutan los multiplicadores de pivotes ya procesados.
            for j in range(row):
                L[row][j], L[chosen][j] = L[chosen][j], L[row][j]
            ctx.emit(
                "permutacion_plu",
                f"Permutar F{row+1} y F{chosen+1}; actualizar las columnas previas de L.",
                {"fila": row, "otra_fila": chosen, "P": P, "L": L, "U": U,
                 "columnas_previas_antes": old_multipliers,
                 "columnas_previas_despues": [L[row][:row], L[chosen][:row]]},
            )
        for i in range(row + 1, m):
            ctx.tick(n)
            entry, pivot = U[i][col], U[row][col]
            multiplier = entry / pivot
            L[i][row] = multiplier
            if multiplier:
                before = U[i][:]
                U[i] = freeze([a - multiplier * x for a, x in zip(before, U[row])])
                ctx.emit(
                    "eliminacion_lu",
                    f"Eliminar debajo del pivote de la columna {col+1}.",
                    {
                        "destino": i,
                        "origen": row,
                        "multiplicador": multiplier,
                        "L": L, "U": U, "pivote": pivot,
                        "fila_antes": before, "fila_despues": U[i],
                    },
                    rf"l_{{{i+1},{row+1}}}=\frac{{{tex(entry)}}}{{{tex(pivot)}}}={tex(multiplier)},\quad "
                    + row_replacement(before, U[row], -multiplier, U[i], i),
                )
        pivots.append(col)
        row += 1
        ctx.progress(row * 90 // max(1, min(m, n)))
    PA, LU = multiply(P, A, ctx), multiply(L, U, ctx)
    product_steps(ctx,L,U,LU,"LU")
    result = {
        "P": P,
        "L": L,
        "U": U,
        "rango": len(pivots),
        "pivotes": pivots,
        "convencion": "PA=LU" if pivoting else "A=LU",
    }
    verification = {
        "kind": "factorizacion",
        "description": "PA=LU, L unitaria inferior y U escalonada.",
        "passed": PA == LU
        and all(
            L[i][i] == 1 and all(L[i][j] == 0 for j in range(i + 1, m))
            for i in range(m)
        ),
        "PA": PA,
        "LU": LU,
    }
    if b is not None:
        solve_from_factors(A, b, result, verification, ctx)
    return result, verification


def reuse_factors(A, b, factors, pivoting, ctx):
    if not isinstance(factors, dict) or not {"L", "U", "P"} <= factors.keys():
        raise InputError("Los factores guardados deben incluir L, U y P.")
    L, U, P = (matrix(factors[key]) for key in ("L", "U", "P"))
    m, n = len(A), len(A[0])
    if len(L) != m or len(L[0]) != m or len(P) != m or len(P[0]) != m or len(U) != m or len(U[0]) != n:
        raise InputError("Las dimensiones de los factores guardados deben coincidir con A.")
    unit = identity(m)
    row_pivots = [next((j for j, value in enumerate(row) if value), n) for row in U]
    nonzero_pivots = [j for j in row_pivots if j < n]
    if (sorted(P) != sorted(unit) or (not pivoting and P != unit)
            or any(L[i][i] != 1 or any(L[i][i+1:]) for i in range(m))
            or row_pivots != sorted(row_pivots) or len(nonzero_pivots) != len(set(nonzero_pivots))):
        raise InputError("Los factores guardados no tienen la forma de una factorización LU o PLU.")
    PA, LU = multiply(P, A, ctx), multiply(L, U, ctx)
    if PA != LU:
        raise InputError("Los factores guardados no corresponden a la matriz A.")
    result = {"L": L, "U": U, "P": P, "convencion": "PA=LU" if pivoting else "A=LU",
              "pivotes": nonzero_pivots, "rango": len(nonzero_pivots), "reutilizo_factores": True}
    verification = {"kind": "factorizacion", "passed": True, "PA": PA, "LU": LU}
    ctx.emit("reutilizar_factores", "Comprobar los factores guardados antes de sustituir.",
             {"PA": PA, "LU": LU}, r"PA=LU" if pivoting else r"A=LU")
    solve_from_factors(A, b, result, verification, ctx)
    return result, verification


def solve_from_factors(A, b, result, verification, ctx):
    L, U, P = (result[key] for key in ("L", "U", "P"))
    m, n = len(A), len(A[0])
    permuted = matvec(P, b, ctx)
    ctx.emit("etapa_L", "Formar la matriz aumentada para la sustitución progresiva.",
             {"matriz": [row + [rhs] for row, rhs in zip(L, permuted)], "separador": m}, r"Ly=Pb")
    y = []
    for i in range(m):
        terms = dot_formula(L[i][:i], y)
        y.append(permuted[i] - sum((L[i][j] * y[j] for j in range(i)), F(0)))
        ctx.emit(
            "sustitucion_L",
            f"Resolver la componente y{i+1} de Ly=Pb.",
            {"componente": i, "valor": y[-1], "y": y},
            rf"y_{{{i+1}}}={tex(permuted[i])}-({terms})={tex(y[-1])}",
        )
    ctx.emit("etapa_U", "Formar la matriz aumentada para la sustitución regresiva.",
             {"matriz": [row + [rhs] for row, rhs in zip(U, y)], "separador": n}, r"Ux=y")
    solution = solve(U, y, ctx, method="gauss")
    result.update(
        {
            "b_permutado": permuted,
            "y": y,
            "sistema": solution,
            "clasificacion": solution["clasificacion"],
            "particular": solution["particular"],
            "direcciones": solution["direcciones"],
            "parametros": solution.get("parametros", []),
        }
    )
    verification["Ly"] = matvec(L, y, ctx)
    verification["passed"] = (
        verification["passed"] and verification["Ly"] == permuted
    )
    if solution["clasificacion"] != "incompatible":
        verification["Axp"] = matvec(A, solution["particular"], ctx)
        verification["Av"] = [matvec(A, v, ctx) for v in solution["direcciones"]]
        verification["passed"] = (
            verification["passed"]
            and verification["Axp"] == b
            and all(not any(v) for v in verification["Av"])
        )
        ctx.emit("verificar_sistema_original", "Sustituir en el sistema original antes de la permutación.",
                 {"Ax": verification["Axp"], "b": b, "Av": verification["Av"]}, r"Ax_p=b,\quad Av_i=0")
    else:
        # El certificado de U se transforma al sistema original: U=L^-1 P A.
        cert = solution["certificado"]
        from .reduction import inverse

        E = multiply(inverse(L, Context(checkpoint=ctx.checkpoint)), P, ctx)
        witness = [
            sum((cert["y"][i] * E[i][j] for i in range(m)), F(0)) for j in range(m)
        ]
        left = [
            sum((witness[i] * A[i][j] for i in range(m)), F(0)) for j in range(n)
        ]
        right = sum((witness[i] * b[i] for i in range(m)), F(0))
        result["certificado_original"] = {"y": witness, "yA": left, "yb": right}
        verification["passed"] = (
            verification["passed"] and not any(left) and right != 0
        )
