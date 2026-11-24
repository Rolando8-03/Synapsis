"""Geometría derivada de cálculos exactos y aplicaciones de matrices."""
from fractions import Fraction as F
from math import cos, pi, sin
import sympy as sp

from .algebra import least_squares, real_display, show, small, step
from motor_matematico.algorithms.linear.context import integer, matrix, tex, vector
from motor_matematico.algorithms.linear.reduction import solve


def intersections(data,ctx):
    A = matrix(data["A"])
    n = len(A[0])
    b = vector(data["b"],len(A))
    if n<2:
        raise ValueError("Ingresá al menos dos incógnitas.")
    result = solve(A,b,ctx)
    result["formula_latex"] = (rf"\operatorname{{rang}}(A)={result['rango_A']},\quad "
                               rf"\operatorname{{rang}}([A\mid b])={result['rango_aumentada']}")
    step(ctx,"rangos","Leer la intersección a partir de ambos rangos exactos.",
         result["formula_latex"], pivotes=[j+1 for j in result["pivotes"]])
    if n==2 and len(A)==2:
        extent = max([4,*(abs(real_display(v))*1.25 for v in result.get("particular") or [])])
        lines = []
        for (a,c), value in zip(A,b):
            if a or c:
                point = [real_display(value/a),0] if abs(a)>=abs(c) else [0,real_display(value/c)]
                greatest = max(abs(a),abs(c))
                dx,dy = real_display(c/greatest),real_display(-a/greatest)
                lines.append([[point[0]+t*dx,point[1]+t*dy] for t in (-extent,extent)])
            else:
                lines.append([])
        formulas = [rf"\left({tex(row[0])}\right)x+\left({tex(row[1])}\right)y={tex(value)}"
                    for row,value in zip(A,b)]
        result["visual_libro"] = {"tipo":"rectas","lineas":lines,"ecuaciones":formulas,
                                  "punto":list(map(real_display,result["particular"])) if result["clasificacion"]=="unica" else None}
        norm = sum(value**2 for value in A[1])
        if norm:
            result["visual_libro"]["control"] = {
                "campo":"b", "indice":1, "eje":"intercepto", "normal":list(map(real_display,A[1])),
                "punto":list(map(real_display,(b[1]*value/norm for value in A[1]))),
                "valor":str(b[1]),"etiqueta":"Término independiente de la segunda recta",
            }
    if n==3:
        planes = []
        for row,value in zip(A,b):
            fixed = max(range(3),key=lambda j:abs(row[j]))
            if row[fixed]==0:
                continue
            free = [j for j in range(3) if j!=fixed]
            plane = []
            for u,v in [(-3,-3),(3,-3),(3,3),(-3,3)]:
                p = [0]*3
                p[free[0]],p[free[1]] = u,v
                p[fixed] = (value-row[free[0]]*u-row[free[1]]*v)/row[fixed]
                plane.append(list(map(real_display,p)))
            planes.append(plane)
        result["visual_libro"] = {"tipo":"planos","planos":planes,
                                  "punto":list(map(real_display,result["particular"])) if result["clasificacion"]=="unica" else None,
                                  "direccion":list(map(real_display,result["direcciones"][0])) if result["clasificacion"]!="incompatible" and len(result.get("direcciones",[]))==1 else None,
                                  "particular":list(map(real_display,result["particular"])) if result.get("particular") is not None else None}
    return result


def transform(data,ctx):
    A = small(data)
    B = small(data,"B")
    v = sp.Matrix(vector(data["v"],2))
    if A.shape!=(2,2) or B.shape!=(2,2) or B.det()==0:
        raise ValueError("Usá una transformación 2×2 y una base 2×2 invertible.")
    Tv, coords = A*v,B.inv()*v
    step(ctx,"base","Resolver Bc=v. Las coordenadas cambian mientras v conserva su posición.",
         r"Bc=v", coordenadas=show(coords), comprobacion=bool(B*coords==v))
    step(ctx,"imagen","Combinar las columnas de la transformación con las componentes de v.",
         r"T(v)=Av", imagen=show(Tv), imagenes_base=show(A*B))
    vectors = [("v",v),("T(v)",Tv),("T(b₁)",A*B[:,0]),("T(b₂)",A*B[:,1])]
    return {"coordenadas":show(coords),"imagen":show(Tv),"imagenes_base":show(A*B),
            "visual_libro":{"tipo":"vectores","vectores":[[label,list(map(real_display,p))] for label,p in vectors],
                            "control":{"campo":"v","eje":"xy","valor":list(map(str,v)),"etiqueta":"Vector v"}}}


def norms(data,ctx):
    v = vector(data["v"],2)
    l1, q, li = sum(map(abs,v)),sum(x*x for x in v),max(map(abs,v))
    l2 = sp.sqrt(q)
    step(ctx,"normas","Sumar valores absolutos, tomar raíz de cuadrados y buscar la mayor componente.",
         r"\|v\|_1=|v_1|+|v_2|,\quad\|v\|_2=\sqrt{v_1^2+v_2^2},\quad\|v\|_\infty=\max_i|v_i|",
         uno=l1, dos=str(l2), infinito=li)
    choice = data["norma"]
    shapes = {"uno":[(1,0),(0,1),(-1,0),(0,-1),(1,0)],
              "dos":[(cos(t*pi/40),sin(t*pi/40)) for t in range(81)],
              "infinito":[(1,1),(-1,1),(-1,-1),(1,-1),(1,1)]}
    if choice not in shapes:
        raise ValueError("Elegí una de las tres normas.")
    return {"norma_1":l1,"norma_2":str(l2),"norma_infinito":li,
            "norma_residual_en_iterativos":"Jacobi, Gauss-Seidel y SOR permiten elegir la norma de trabajo.",
            "visual_libro":{"tipo":"contorno","lineas":[shapes[choice]],"etiqueta":"Frontera de la bola unitaria",
                             "selector":["norma","Bola unitaria",[["uno","Norma 1"],["dos","Norma 2"],["infinito","Norma infinito"]],choice],
                             "enlace":["#iterativos/iterativos.jacobi","Usar normas en Jacobi"]}}


def oriented_area(data,ctx):
    A = small(data)
    if A.shape!=(2,2):
        raise ValueError("El área orientada corresponde a dos columnas de dos componentes.")
    u,v = A[:,0],A[:,1]
    determinant = u[0]*v[1]-u[1]*v[0]
    orientation = "antihoraria" if determinant>0 else "horaria" if determinant<0 else "dependiente"
    step(ctx,"area","Restar los dos productos cruzados y leer el signo.",
         rf"\det A=({u[0]})({v[1]})-({u[1]})({v[0]})={sp.latex(determinant)}", orientacion=orientation)
    polygon = [list(map(real_display,p)) for p in (sp.zeros(2,1),u,u+v,v,sp.zeros(2,1))]
    return {"determinante":str(determinant),"area":str(abs(determinant)),"orientacion":orientation,
            "visual_libro":{"tipo":"contorno","lineas":[polygon],"puntos":[list(map(real_display,v))],
                             "control":{"campo":"A","indice":1,"eje":"columna","valor":list(map(str,v)),"etiqueta":"Segunda columna"}}}


def points_from(data, minimum=2, maximum=12, distinct=True):
    points = matrix(data["puntos"])
    if not minimum<=len(points)<=maximum or len(points[0])!=2:
        raise ValueError(f"Ingresá entre {minimum} y {maximum} pares (x, y).")
    if distinct and len({x for x,y in points})!=len(points):
        raise ValueError("Las abscisas deben ser distintas.")
    return points


def regression(data,ctx):
    points = points_from(data,maximum=20,distinct=False)
    A,b = sp.Matrix([[1,x] for x,y in points]),sp.Matrix([y for x,y in points])
    c,r,directions,method = least_squares(A,b,ctx)
    squared = r.dot(r)
    lo, hi = min(x for x,y in points),max(x for x,y in points)
    if lo==hi:
        lo,hi = lo-1,hi+1
    line = [[real_display(x),real_display(c[0]+c[1]*x)] for x in (lo,hi)]
    marks = [list(map(real_display,p)) for p in points]
    segments = [[point,[point[0],real_display(c[0]+c[1]*original[0])]] for point,original in zip(marks,points)]
    step(ctx,"suma","Elevar al cuadrado los residuos y sumarlos.",r"S=\sum_i (y_i-\hat y_i)^2="+sp.latex(squared))
    return {"intercepto":str(c[0]),"pendiente":str(c[1]),"residuos":show(r),"suma_cuadratica":str(squared),
            "unica":not directions,"direcciones":directions,"metodo":method,
            "visual_libro":{"tipo":"regresion","lineas":[line,*segments],"puntos":marks,
                            "control":{"campo":"puntos","eje":"punto","valores":[list(map(str,p)) for p in points],
                                       "etiqueta":"Punto observado"}}}


def markov(data,ctx):
    P = small(data,"A",square=True)
    if P.rows < 2:
        raise ValueError("Ingresá una cadena de al menos dos estados para comparar con un ciclo.")
    state = sp.Matrix(vector(data["b"],P.rows))
    steps = integer(data["pasos"],"Pasos",1,24)
    if any(v<0 for v in P) or any(sum(P[:,j])!=1 for j in range(P.cols)) or any(v<0 for v in state) or sum(state)!=1:
        raise ValueError("Cada columna de P y el estado inicial deben sumar 1 con entradas no negativas.")
    def period(M):
        reach = sp.Matrix(M.rows,M.cols,lambda i,j:int(bool(M[i,j]>0)))
        reach_power = reach.copy()
        limit = max(1,(M.rows-1)**2+1)
        for k in range(1,limit+1):
            if all(v>0 for v in reach_power):
                return k
            reach_power = (reach_power*reach).applyfunc(lambda v: int(bool(v>0)))
        return None
    def trajectory(M,label):
        p = state.copy()
        history = [[0,*map(str,p)]]
        for k in range(1,steps+1):
            p = M*p
            history.append([k,*map(str,p)])
            step(ctx,"evolucion",f"{label}: multiplicar por P para obtener el estado {k}.",
                 rf"p_{{{k}}}=Pp_{{{k-1}}}", estado=list(map(str,p)), suma=str(sum(p)))
        return history
    cyclic = sp.zeros(P.rows)
    for i in range(P.rows):
        cyclic[(i+1)%P.rows,i] = 1
    first, second = trajectory(P,"Cadena ingresada"),trajectory(cyclic,"Ciclo de comparación")
    exponent = period(P)
    step(ctx,"clasificacion","Verificar si alguna potencia tiene todas las entradas positivas.",
         exponente_positivo=exponent, periodo_del_ciclo=P.rows)
    return {"regular":exponent is not None,"primera_potencia_positiva":exponent,"periodo_del_ciclo":P.rows,
            "ciclo":show(cyclic),"cadena":first,"comparacion_periodica":second,
            "series":{"points":[[a[0],float(F(a[1])),float(F(b[1]))] for a,b in zip(first,second)],
                      "names":["Prob. estado 1 de P","Prob. estado 1 del ciclo"]}}
