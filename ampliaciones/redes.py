"""Aplicaciones visuales de matrices en redes y códigos."""
from fractions import Fraction as F
from math import cos, pi, sin

from .algebra import step
from motor_matematico.algorithms.linear.context import integer, matrix, vector
from motor_matematico.algorithms.linear.reduction import solve


def graph_data(data, *, limit=10):
    A = matrix(data["A"],square=True)
    n = len(A)
    if not 2<=n<=limit or any(A[i][i]!=0 for i in range(n)) or any(value<0 for row in A for value in row):
        raise ValueError(f"Usá 2 a {limit} vértices, diagonal nula y pesos no negativos. Cero indica que no hay arista.")
    return A,n


def scene(A, *, directed=False, path=()):
    n = len(A)
    labels = [str(i+1) for i in range(n)]
    p = [(cos(2*pi*i/n),sin(2*pi*i/n)) for i in range(n)]
    selected = set(zip(path,path[1:]))
    edges = [[i,j,str(w),(i,j) in selected] for i,row in enumerate(A)
             for j,w in enumerate(row) if w and (directed or i<j)]
    return {"tipo":"grafo","vertices":p,"etiquetas":labels,"aristas":edges,"dirigido":directed}


def circuits(data,ctx):
    A,n = graph_data(data)
    if any(A[i][j]!=A[j][i] for i in range(n) for j in range(n)):
        raise ValueError("En una red de conductancias la matriz de pesos debe ser simétrica.")
    b = vector(data["b"],n)
    if sum(b)!=0:
        raise ValueError("Las corrientes externas deben sumar cero.")
    L = [[sum(A[i]) if i==j else -A[i][j] for j in range(n)] for i in range(n)]
    step(ctx,"kirchhoff","Usar la suma de conductancias en la diagonal y fijar el último potencial a cero.",
         r"\sum_j g_{ij}(V_i-V_j)=I_i", laplaciana=L, inyecciones=b)
    r = solve([row[:-1] for row in L[:-1]],b[:-1],ctx)
    if r["clasificacion"]!="unica":
        raise ValueError("Conectá todos los nodos a la referencia para obtener potenciales únicos.")
    V = [*r["particular"],F(0)]
    currents = [[i+1,j+1,A[i][j]*(V[i]-V[j])] for i in range(n) for j in range(i+1,n) if A[i][j]]
    proof = [sum(A[i][j]*(V[i]-V[j]) for j in range(n)) for i in range(n)]
    formulas = {f"{i+1}-{j+1}": str(A[i][j]*(V[i]-V[j])) for i in range(n) for j in range(i+1,n) if A[i][j]}
    visual = scene(A)
    visual["aristas"] = [[i,j,f"g={g}, I={formulas[f'{i+1}-{j+1}']}",highlight]
                         for i,j,g,highlight in visual["aristas"]]
    step(ctx,"balance","Verificar la corriente neta de cada nodo con los potenciales hallados.",
         r"LV=I", corrientes_calculadas=proof)
    return {"potenciales":V,"tabla":currents,"encabezados":["Desde","Hasta","Corriente con signo"],
            "verificacion":proof==b,"visual_libro":visual}


def shortest(data,ctx):
    A,n = graph_data(data)
    start, goal = (integer(data[key],key.capitalize(),1,n)-1 for key in ("origen","destino"))
    distance = {start:F(0)}
    pending = set(range(n))
    parent = {}
    while pending.intersection(distance):
        i = min(pending.intersection(distance),key=lambda j:(distance[j],j))
        pending.remove(i)
        step(ctx,"vertice",f"Fijar la distancia del vértice {i+1} al extraer el menor peso pendiente.",
             vertice=i+1, distancia=distance[i])
        for j,w in enumerate(A[i]):
            if j not in pending or not w:
                continue
            candidate = distance[i]+w
            improve = j not in distance or candidate<distance[j]
            if improve:
                distance[j],parent[j] = candidate,i
            step(ctx,"arista",f"Probar la arista {i+1} → {j+1}.",
                 r"d(j)\gets\min(d(j),d(i)+w_{ij})", precio=w, candidato=candidate, actualiza=improve)
        if i==goal:
            break
    path = []
    if goal in distance:
        current = goal
        path = [current]
        while current!=start:
            current = parent[current]
            path.insert(0,current)
    return {"camino":[i+1 for i in path],"distancia":distance.get(goal),
            "alcanzable":bool(path),"visual_libro":scene(A,directed=True,path=path)}


def binary(data,ctx):
    A = matrix(data["A"])
    m,n = len(A),len(A[0])
    word, error = (vector(data[key],n) for key in ("b","error"))
    if max(m,n)>10 or any(v not in (0,1) for v in (*word,*error,*(v for row in A for v in row))):
        raise ValueError("Usá una matriz binaria de hasta 10×10 y dos vectores binarios compatibles.")
    received = [(x+y)%2 for x,y in zip(word,error)]
    original = [sum(a*x for a,x in zip(row,word))%2 for row in A]
    if any(original):
        raise ValueError("La palabra original debe ser válida: Hc = 0 módulo 2.")
    syndrome = []
    for i,row in enumerate(A):
        products = [a*x for a,x in zip(row,received)]
        answer = sum(products)%2
        syndrome.append(answer)
        step(ctx,"sindrome",f"Multiplicar la fila de paridad {i+1} por la palabra recibida.",
             rf"s_{{{i+1}}}=H_{{{i+1},:}}r\pmod 2", productos=products, bit=answer)
    vertices = [[-1,1-2*i/max(1,n-1)] for i in range(n)]+[[1,1-2*i/max(1,m-1)] for i in range(m)]
    edges = [[j,n+i,"1",bool(received[j])] for i,row in enumerate(A) for j,v in enumerate(row) if v]
    return {"recibida":received,"sindrome":syndrome,"error_detectado":any(syndrome),
            "interpretacion":"Un síndrome nulo puede corresponder a un error indetectable por H.",
            "visual_libro":{"tipo":"grafo","vertices":vertices,"aristas":edges,
                            "etiquetas":[f"r{i+1}={v}" for i,v in enumerate(received)]+[f"s{i+1}={v}" for i,v in enumerate(syndrome)]}}
