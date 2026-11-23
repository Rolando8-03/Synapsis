"""Convierte estados reales de la ejecución en pasos de lectura para Synapsis."""
from fractions import Fraction
import ast

from motor_matematico.algorithms.linear.context import Context, matrix, tex, vector
from motor_matematico.parsing.numbers import parse_number
from motor_matematico.algorithms.linear.worked import dot_formula, parenthesize, product_steps
from motor_matematico.algorithms.calculo import analizar, evaluar


def original_rows(ctx, steps):
    for step in steps:
        data = {"matriz":step["matriz"],"separador":len(step["matriz"][0])-1} if step["mostrar_matriz"] else {}
        ctx.emit("fila_original",step["titulo"],data,step.get("formula_latex",""))


def legacy_trace(op, out, ctx):
    if op == "original.sistema":
        ctx.emit("metodo", "Comenzar la fase de Gauss.", {})
        original_rows(ctx, out["pasos_gauss"])
        if out.get("objetivo") == "escalonada":
            return
        ctx.emit("metodo", "Comenzar la fase de Gauss-Jordan.", {})
        original_rows(ctx, out["pasos_jordan"])
        for step in out.get("pasos_sustitucion", []):
            variable, expression = step["variable"] + 1, step["expresion"]
            terms = [tex(expression["constante"])]
            terms.extend(rf"\left({tex(coef)}\right)x_{{{int(index)+1}}}"
                         for index, coef in expression["terminos"].items() if coef != "0")
            ctx.emit("sustitucion_regresiva", f"Despejar x{variable} por sustitución regresiva.",
                     {}, rf"x_{{{variable}}}=" + "+".join(terms))
        if out.get("latex_solucion"):
            ctx.emit("solucion","Despejar y parametrizar las variables libres.",{},out["latex_solucion"])
        else:
            ctx.emit("contradiccion","La fila contradictoria prueba la incompatibilidad.",
                     {"fila":out.get("fila_contradiccion_datos")})
        for i, proof in enumerate(out.get("comprobaciones") or [],1):
            actual, expected = proof["resultado"], proof["esperado"]
            ctx.emit("sustitucion",f"Sustituir la solución particular en la ecuación {i}.",proof,
                     dot_formula(out["A"][i-1],out["solucion_particular"])+f"={tex(actual)}={tex(expected)}")
    elif op == "original.inversa_adjunta":
        ctx.emit("determinante","Calcular el determinante y diagnosticar invertibilidad.",out["procedimiento_determinante"],
                 r"\det(A)="+tex(out["determinante"]))
        for detail in out.get("detalle_cofactores",[]):
            i,j=detail["fila"],detail["columna"]
            ctx.emit("cofactor",f"Eliminar la fila {i} y la columna {j} y evaluar el menor.",detail,
                     rf"C_{{{i},{j}}}=(-1)^{{{i+j}}}({tex(detail['det_menor'])})={tex(detail['cofactor'])}")
        if out.get("adjunta"):
            ctx.emit("adjunta","Transponer la matriz de cofactores.",{"cofactores":out["cofactores"],"adjunta":out["adjunta"]},
                     r"\operatorname{adj}(A)=C^{\mathsf T}")
            ctx.emit("inversa","Multiplicar cada entrada de la adjunta por el recíproco del determinante.",
                     {"reciproco":out["reciproco_determinante"],"inversa":out["inversa_adjunta"]},
                     r"A^{-1}=\frac{\operatorname{adj}(A)}{\det(A)}")
            product_steps(ctx,out["A"],out["inversa"],out["producto"],r"AA^{-1}")
            product_steps(ctx,out["inversa"],out["A"],out["producto_izquierdo"],r"A^{-1}A")
    elif op == "original.triangular":
        for key,label in (("etapa_Ly","Ly=b"),("etapa_Ux","Ux=y")):
            phase=out[key]
            ctx.emit("etapa",f"Construir el sistema {label}.",{"matriz":phase["inicial"],"separador":len(phase["inicial"][0])-1},label)
            for step in phase["pasos"]:
                ctx.emit("fila",step["descripcion"],{"matriz":step["matriz"],"separador":len(step["matriz"][0])-1})
            ctx.emit("fin_etapa","Leer el sistema equivalente.",{"matriz":phase["reducida"],"separador":len(phase["reducida"][0])-1})
        product_steps(ctx,out["L"],out["U"],out["producto_LU"],"LU")
        if out["solucion"] is not None:
            check = [row[0] for row in out["comprobacion"]]
            matvec_steps(ctx,out["A"],out["solucion"],check,"Ax")
    elif op in ("original.propiedades_det","matrices.propiedades"):
        for prop in out["propiedades"]:
            label = prop["nombre"]
            ctx.emit("igualdad",f"Calcular y comparar ambos miembros de {label}.",prop)
        for prop in out.get("comparaciones_no_generales",[]):
            ctx.emit("comparacion","Examinar la comparación que depende de las matrices ingresadas.",prop)
        if "suma_determinantes" in out:
            ctx.emit("contraejemplo","Comparar det(A+B) con det(A)+det(B).",out["suma_determinantes"])
    elif op == "original.relaciones":
        ctx.emit("suma","Sumar u y v componente a componente.",{"u":out["u"],"v":out["v"],"suma":out["u_mas_v"]})
        for vec, res, label in (("u","Au","Au"),("v","Av","Av"),("u_mas_v","Au_mas_v","A(u+v)"),("cu","Acu","A(cu)")):
            matvec_steps(ctx,out["A"],out[vec],out[res],label)
        for prop in out["propiedades"]:
            ctx.emit("igualdad","Comparar los miembros de "+prop["nombre"]+".",prop)


def matvec_steps(ctx,A,v,w,label):
    for i,(row,value) in enumerate(zip(A,w),1):
        ctx.emit("matriz_vector",f"Multiplicar la fila {i} por el vector.",{"fila":row,"vector":v,"valor":value},
                 rf"({label})_{{{i}}}={dot_formula(row,v)}={tex(value)}")


def original_extra(op, data, result, ctx):
    if op in ("vectores.combinacion","vectores.paralelogramo"):
        u,v=vector(data["u"]),vector(data["v"])
        a,b=parse_number(data["alpha"]),parse_number(data["beta"])
        for i,(x,y,value) in enumerate(zip(u,v,result.get("vector",result.get("vector_resultante"))),1):
            ctx.emit("combinacion",f"Escalar, sumar y leer la componente {i}.",{},
                     rf"w_{{{i}}}={parenthesize(a)}{parenthesize(x)}+{parenthesize(b)}{parenthesize(y)}={tex(value)}")
    elif op=="vectores.angulo":
        u,v=vector(data["u"]),vector(data["v"])
        ctx.emit("producto_punto","Obtener los productos interiores de los dos vectores.",{},
                 r"u\cdot v="+dot_formula(u,v)+"="+tex(result["producto_punto"]))
        ctx.emit("normas","Calcular las normas y dividir el producto punto por su producto.",{"coseno":result["coseno"]},
                 r"\cos\theta=\frac{u\cdot v}{\sqrt{"+dot_formula(u,u)+r"}\sqrt{"+dot_formula(v,v)+r"}}")
        ctx.emit("angulo","Aplicar el arcocoseno y convertir a grados.",{"grados":result["angulo_grados"]},
                 r"\theta=\arccos(\cos\theta)\,\frac{180^\circ}{\pi}")
    elif op.startswith("grafica."):
        ctx.emit("dominio","Elegir el intervalo del modelo y muestrear su dominio real.",
                 {"desde":data["from"],"hasta":data["to"],"expresion":data["expr"]})
        for t,x,y in result["muestras"]:
            ctx.emit("muestra","Sustituir el parámetro o la abscisa y ubicar el punto.",{"parametro":t,"x":x,"y":y})
    elif op=="bases.romanos":
        text=result.get("romano",result.get("representacion"))
        values={"I":1,"IV":4,"V":5,"IX":9,"X":10,"XL":40,"L":50,"XC":90,"C":100,"CD":400,"D":500,"CM":900,"M":1000}
        import re
        tokens=re.findall(r"CM|CD|XC|XL|IX|IV|[IVXLCDM]",text)
        for token in tokens:
            ctx.emit("romano","Leer el grupo "+token+".",{"grupo":token,"valor":values[token]})
        ctx.emit("romano_suma","Sumar los valores de los grupos.",{},'+'.join(str(values[t]) for t in tokens)+'='+str(sum(values[t] for t in tokens)))
    elif op=="matrices.comparar":
        A,B=matrix(data["A"]),matrix(data["B"])
        for key,left,right in (("AB",A,B),("BA",B,A)):
            if key in result:
                product_steps(ctx,left,right,result[key],key)
        ctx.emit("comparar","Comparar dimensiones y entradas de los resultados.",{"iguales":result["iguales"],"conmutan":result.get("conmutan")})


def error_trace(op, data, out, ctx):
    if op=="errores.redondeo":
        ctx.emit("escala","Mover el corte decimal a una posición entera.",{"valor_exacto":data["numero"],"decimales":data["decimales"]},r"y=|x|\,10^d")
        ctx.emit("redondeo","Truncar hacia cero. Para redondear, aplicar el ajuste de media unidad.",{"truncado":out["truncado"],"redondeado":out["redondeado"]})
        ctx.emit("tolerancia","Evaluar la tolerancia porcentual de las cifras pedidas.",{"cifras":data["cifras"],"tolerancia":out["tolerancia_porcentual"]},out["formula_latex"])
    elif op=="errores.propagacion":
        for title, keys, formula in (
            ("Evaluar la derivada en el punto de referencia.",("derivada","metodo"),r"f'(x)"),
            ("Multiplicar la derivada por la perturbación.",("diferencial",),out["formula_latex"]),
            ("Evaluar la diferencia real y restar la aproximación lineal.",("variacion","error_absoluto"),r"|f(x+\Delta x)-f(x)-f'(x)\Delta x|"),
        ):
            ctx.emit("propagacion",title,{"x":data["x"],"delta":data["delta"],**{k:out[k] for k in keys}},formula)
    elif op in ("errores.acumulacion","errores.taylor"):
        ctx.emit("modelo","Establecer el modelo y la precisión elegida.",data,out["formula_latex"])
        for row in out["tabla"]:
            ctx.emit("termino",f"Obtener {'el término' if op.endswith('taylor') else 'la fila del período'} {row[0]}.",
                     dict(zip(out["encabezados"],row)))
        ctx.emit("comparar","Comparar el resultado retenido con la referencia.",{k:v for k,v in out.items()
                    if k not in {"tabla","encabezados","series","formula_latex"}})
    elif op=="errores.exactitud":
        values=vector(data["mediciones"])
        mean=out["promedio"]
        ctx.emit("media","Sumar las mediciones y dividir por su cantidad.",{"promedio":mean},
                 r"\bar{x}=\frac{"+'+'.join(parenthesize(v) for v in values)+r"}{"+str(len(values))+"}="+tex(mean))
        ctx.emit("dispersion","Restar el promedio a cada observación y sumar los cuadrados.",{"desviaciones":[v-mean for v in values],"varianza":out["varianza_muestral"]},
                 r"s^2=\frac{\sum_i(x_i-\bar{x})^2}{n-1}")
        ctx.emit("sesgo","Restar la referencia al promedio y calcular la desviación estándar.",
                 {"referencia":data["referencia"],"sesgo":out["sesgo"],"desviacion":out["desviacion_estandar_muestral"]})
    elif op=="errores.maquina":
        ctx.emit("limites","Consultar la precisión y los extremos del formato binario de Python.",
                 {k:out[k] for k in ("epsilon","maximo_finito","minimo_normal","minimo_subnormal")})
        ctx.emit("ejemplos_flotantes","Probar la suma binaria y los extremos del formato.",
                 out["demostraciones"],r"0.1+0.2\approx0.30000000000000004")
        ctx.emit("cancelacion","Evaluar la resta directa y racionalizarla multiplicando por su conjugado.",
                 {"directa":out["resta_directa"],"racionalizada":out["forma_racionalizada"]},out["formula_latex"])


def calculus_trace(op, data, out, ctx):
    expression=data["expresion"]
    if op=="calculadora.evaluar":
        tree=analizar(expression)
        args=(0,parse_number(data.get("ans","0")),data.get("grados",False))
        def walk(part):
            for child in ast.iter_child_nodes(part):
                if isinstance(child,(ast.BinOp,ast.UnaryOp,ast.Call)): walk(child)
            if isinstance(part,(ast.BinOp,ast.UnaryOp,ast.Call)) or part is tree:
                ctx.emit("expresion","Evaluar la subexpresión después de sus operandos.",
                         {"expresion":ast.unparse(part),"valor":evaluar(part,*args)})
        walk(tree)
        return
    if op=="calculo.definida":
        from motor_matematico.algorithms.calculo import integrar
        try:
            primitive=integrar(analizar(expression,variable=True))
        except ValueError:
            ctx.emit("metodo","Evaluar con la aproximación numérica seleccionada.",{"expresion":expression, "valor":out.get("valor")})
            return
        ctx.emit("primitiva","Obtener una primitiva en el intervalo.",{"F":primitive})
        ctx.emit("extremos","Sustituir los dos límites y restar los valores de la primitiva.",data,r"\int_a^b f(x)\,dx=F(b)-F(a)")
        return
    tree=analizar(expression,variable=True)
    derivative=op=="calculo.derivar"
    from motor_matematico.algorithms.calculo import derivar, integrar
    rule=derivar if derivative else integrar
    def trace(part):
        if isinstance(part,ast.BinOp) and isinstance(part.op,(ast.Add,ast.Sub)):
            trace(part.left)
            trace(part.right)
        try:
            value=rule(part)
        except ValueError:
            return
        if isinstance(part,ast.BinOp):
            label={ast.Add:"linealidad de la suma",ast.Sub:"linealidad de la resta",ast.Pow:"potencia",ast.Mult:"producto o factor constante",ast.Div:"cociente o factor constante"}[type(part.op)]
        elif isinstance(part,ast.Call): label="función elemental y su argumento"
        else: label="constante o variable"
        ctx.emit("regla",f"Aplicar la regla de {label}.",{"entrada":ast.unparse(part),"salida":value})
    trace(tree)
    ctx.emit("expresion_final","Leer la expresión obtenida.",{"expresion":out["expresion"]})


def compare_iterations(data, ctx):
    """Compara Jacobi y Gauss-Seidel con los mismos datos y criterio."""
    from decimal import localcontext
    from motor_matematico.algorithms.linear.reduction import solve
    from motor_matematico.algorithms.numerical.iterative import iterative
    from motor_matematico.algorithms.numerical.functions import decimal
    from curso import dominance

    settings = {k:v for k,v in data.items() if k not in {"reordenar"}}
    diagnosis=dominance(settings,ctx)
    if data.get("reordenar") and diagnosis.get("matriz_reordenada"):
        settings["A"]=diagnosis["matriz_reordenada"]
        settings["b"]=diagnosis["b_reordenado"]
    A=matrix(settings["A"],square=True)
    b=vector(settings["b"],len(A))
    reference=solve(A,b,Context(collect_steps=False),trace=False)
    if any(not row[i] for i,row in enumerate(A)):
        raise ValueError("La diagonal contiene ceros. Activá el reordenamiento si existe una permutación dominante.")
    if reference["clasificacion"]=="unica":
        settings.setdefault("referencia",reference["particular"])
    methods={}
    with localcontext() as arithmetic:
        arithmetic.prec=40
        for method in ("jacobi","gauss_seidel"):
            ctx.emit("metodo", "Iniciar "+("Jacobi" if method=="jacobi" else "Gauss-Seidel")+" con la misma semilla.",{})
            result,status,warnings=iterative(method,settings,ctx)
            methods[method]=(result,status,warnings)
    first,second=(item[0] for item in methods.values())
    records=[{row["iteracion"]:row for row in r["tabla"]} for r in (first,second)]
    # Elegir la métrica junto al criterio para que las dos series sean comparables.
    metric={"relativo_vectorial":"error_aproximado_relativo","solo_residual":"norma_residual",
            "porcentaje_por_componente":"error_por_componente_pct"}.get(settings.get("criterio"),"error_aproximado_absoluto")
    def amount(row):
        value=row.get(metric)
        if isinstance(value,list):
            value=max((v for v in value if v is not None),default=None)
        return float(decimal(value)) if value is not None else None
    points=[[i,*[amount(table.get(i,{})) for table in records]]
            for i in sorted(set(records[0]) | set(records[1]))]
    labels=["Jacobi","Gauss-Seidel"]
    ranking=[label for label,r in zip(labels,(first,second)) if r["convergencia"]]
    if len(ranking)==2:
        ranking=["Empate"] if first["iteraciones"]==second["iteraciones"] else [
            labels[int(second["iteraciones"] < first["iteraciones"])]]
    difference=[a-b for a,b in zip(first["vector"],second["vector"])]
    ctx.emit("comparar","Comparar convergencia, número de iteraciones y diferencia de los vectores.",
             {"diferencia":difference,"menos_iteraciones":ranking})
    return {"referencia_exacta":reference.get("particular"),"diagnostico":diagnosis,
            "diferencia":difference,"menos_iteraciones":ranking,"medida_del_grafico":metric,
            "jacobi":{k:v for k,v in first.items() if k!="tabla"},
            "gauss_seidel":{k:v for k,v in second.items() if k!="tabla"},
            "encabezados":["k","Jacobi xₖ","Gauss-Seidel xₖ","Error Jacobi","Error Gauss-Seidel"],
            "tabla":[[i,*[table.get(i,{}).get("vector_decimal") for table in records],*values]
                     for i,*values in points],
            "series":{"points":points,"names":labels}}


def root_visual(data, out):
    """Muestreo Python para mostrar aproximaciones y algunas tangentes de Newton."""
    from math import isfinite
    from decimal import Decimal, localcontext
    from motor_matematico.algorithms.numerical.functions import Function
    from motor_matematico.domain.models import DomainError
    f=Function(data["expresion"],Context())
    table=out["tabla"]
    rows=table
    def real(value):
        return float(Fraction(value))
    middle=real(out["aproximacion"])
    seeds=[middle,*[real(row.get("x_anterior",row["x"])) for row in rows]]
    if out.get("intervalo_inicial"):
        begin,end=map(real,out["intervalo_inicial"])
    else:
        begin,end=min(seeds),max(seeds)
        margin=max((end-begin)*.12,abs(middle)*.04,.25)
        begin,end=begin-margin,end+margin
    if not isfinite(begin) or not isfinite(end) or abs(begin)+abs(end)>1e12:
        return None
    points,tangents,markers,iterations=[],[],[],[]
    with localcontext() as arithmetic:
        arithmetic.prec=26
        for i in range(801):
            x=begin+(end-begin)*i/800
            try:
                y=float(f.value(Decimal(str(x))))
                points.append([x,y if isfinite(y) else None])
            except (DomainError, ArithmeticError,ValueError):
                points.append([x,None])
    for row in rows:
        if "derivada_x" in row:
            left,top,new=real(row["x_anterior"]),real(row["f_anterior_actual"]),real(row["x"])
            # Para Newton modificado el punto de la tangente en y=0 es diferente del iterado.
            slope = real(row["derivada_x"])
            if slope:
                intercept = left - top / slope
                tangents.append([[left, top], [intercept, 0]])
            markers.append([new,0])
        else:
            markers.append([real(row["x"]),real(row["fx"])])
        iterations.append([row["iteracion"], *markers[-1]])
    return {"points":points,"tangents":tangents,"markers":[*markers,[middle,0]], "iteraciones": iterations,
            "caption":"Función, aproximaciones y tangentes de Newton" if tangents else "Función y aproximaciones"}


def compare_bisection(data, output):
    """Obtiene un contraste independiente sobre el intervalo verificado."""
    from decimal import Decimal, localcontext
    from math import isfinite
    from motor_matematico.algorithms.numerical.functions import Function

    f=Function(data["expresion"],Context())
    a,b=map(lambda value:float(Fraction(value)),output["intervalo_inicial"])
    if not (isfinite(a) and isfinite(b) and a<b):
        return None
    with localcontext() as arithmetic:
        arithmetic.prec=40
        def function(x):
            return float(f.value(Decimal(str(x))))
        try:
            from scipy.optimize import bisect
            reference=bisect(function,a,b,xtol=1e-13,maxiter=250)
            source="SciPy · scipy.optimize.bisect"
        except ImportError:
            from mpmath import mp
            arithmetic_mp=mp.clone()
            with arithmetic_mp.workdps(24):
                reference=float(arithmetic_mp.findroot(function,(a,b),solver="bisect",
                                                       tol=arithmetic_mp.mpf("1e-13"),maxsteps=200))
            source="mpmath · bisección de referencia"
        approximation=float(Fraction(output["aproximacion"]))
    return {"motor_de_referencia":source,"raiz_de_referencia":reference,
            "diferencia_absoluta":abs(approximation-reference)}
