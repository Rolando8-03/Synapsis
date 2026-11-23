"""Desarrollos evaluables para las entradas de matrices y vectores."""
from .context import tex


def parenthesize(value):
    return r'\left(' + tex(value) + r'\right)'


def dot_formula(left, right):
    return '+'.join(parenthesize(a) + r'\cdot' + parenthesize(b) for a,b in zip(left,right)) or '0'


def product_steps(ctx, A, B, C, label='AB'):
    """Registrar cada producto punto usando el resultado real del motor."""
    if not ctx.collect_steps:
        return
    ctx.emit('dimension_producto', 'Verificar que las dimensiones internas coinciden.',
             {'dimensiones_A':[len(A),len(A[0])], 'dimensiones_B':[len(B),len(B[0])],
              'dimensiones_resultado':[len(C),len(C[0])]},
             rf'({len(A)}\times {len(A[0])})({len(B)}\times {len(B[0])})\mapsto {len(C)}\times {len(C[0])}')
    columns = list(zip(*B))
    for i, row in enumerate(A):
        formulas = [rf'({label})_{{{i+1},{j+1}}}&={dot_formula(row,column)}={tex(value)}'
                    for j,(column,value) in enumerate(zip(columns,C[i]))]
        ctx.emit('fila_producto', f'Desarrollar todas las entradas de la fila {i+1}.', {'fila_resultante':C[i]},
                 r'\begin{aligned}' + r'\\'.join(formulas) + r'\end{aligned}')


def entry_steps(ctx, A, C, operation, B=None, k=None):
    """Presentar cada entrada de una suma, escala o transposición."""
    if not ctx.collect_steps:
        return
    for i,row in enumerate(C):
        formulas=[]
        for j,value in enumerate(row):
            if operation == 'transpuesta':
                right = rf'a_{{{j+1},{i+1}}}'
            elif operation == 'escalar':
                right = parenthesize(k)+r'\cdot'+parenthesize(A[i][j])
            else:
                sign = '+' if operation == 'suma' else '-'
                right = parenthesize(A[i][j])+sign+parenthesize(B[i][j])
            formulas.append(rf'c_{{{i+1},{j+1}}}&={right}={tex(value)}')
        ctx.emit('entradas_matriz', f'Calcular las entradas de la fila {i+1}.', {'fila_resultante':row},
                 r'\begin{aligned}' + r'\\'.join(formulas) + r'\end{aligned}')


def vector_steps(ctx, operation, u, v, result, k=None):
    if not ctx.collect_steps:
        return
    if operation == 'producto_punto':
        ctx.emit('producto_punto','Multiplicar las parejas y sumar sus productos.', {'terminos':result['terminos']},
                 r'u\cdot v=' + dot_formula(u,v) + '=' + tex(result['valor']))
        return
    if operation == 'norma':
        ctx.emit('norma','Elevar cada componente al cuadrado, sumar y tomar la raíz no negativa.', {},
                 r'\|u\|=\sqrt{' + dot_formula(u,u) + r'}=\sqrt{' + tex(result['norma_cuadrada']) + '}')
        return
    if operation == 'proyeccion':
        ctx.emit('proyeccion_componente','Calcular por separado los dos productos que aparecen en el coeficiente.', {},
                 r'c=\frac{' + dot_formula(u,v) + '}{' + dot_formula(v,v) + '}=' + tex(result['coeficiente']))
        for i,(a,b,p,o) in enumerate(zip(u,v,result['proyeccion'],result['componente_ortogonal']),1):
            ctx.emit('componente',f'Proyectar y restar en la componente {i}.', {},
                     rf'p_{{{i}}}={parenthesize(result["coeficiente"])}\cdot{parenthesize(b)}={tex(p)},\quad '
                     rf'(u-p)_{{{i}}}={parenthesize(a)}-{parenthesize(p)}={tex(o)}')
        return
    for i,value in enumerate(result['vector']):
        if operation in ('suma','resta'):
            sign='+' if operation == 'suma' else '-'
            right=parenthesize(u[i])+sign+parenthesize(v[i])
        elif operation == 'escalar':
            right=parenthesize(k)+r'\cdot'+parenthesize(u[i])
        else:
            j,h=(i+1)%3,(i+2)%3
            right=dot_formula([u[j]],[v[h]])+'-'+dot_formula([u[h]],[v[j]])
        ctx.emit('componente',f'Calcular la componente {i+1}.', {},
                 rf'w_{{{i+1}}}={right}={tex(value)}')


def row_replacement(before, source, factor, after, row):
    formulas = [
        rf"a'_{{{row+1},{j}}}&={parenthesize(a)}+{parenthesize(factor)}{parenthesize(b)}={tex(c)}"
        for j, (a, b, c) in enumerate(zip(before, source, after), 1)
    ]
    return r'\begin{aligned}' + r'\\'.join(formulas) + r'\end{aligned}'
