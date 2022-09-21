import pandas as pd
import numpy as np
from mip import Model, INTEGER, BINARY, xsum, MAXIMIZE
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import random
from itertools import product
import dash_core_components as dcc
import dash_html_components as html

def optimiza(datos,horaIni,horaFin,lineasSimultaneas,lineasDisp):
    
    #introduzco
    inicio = datetime.combine(datetime.today(),datetime.strptime(horaIni+':00','%H:%M:%S').time())
    fin = datetime.combine(datetime.today(),datetime.strptime(horaFin+':00','%H:%M:%S').time())
    tiempoLinea = (fin-inicio).seconds/60

    #numero de productos y lineas
    ni = len(datos.index)
    nj = 4
    
    #producciones maximas
    maxi = datos['PRODMAX'].to_numpy()
    mini = datos['PRODMIN'].to_numpy()

    #tiempos de limpieza + preparacion
    tpi = (datos['TPREP']).tolist()

    #division en k franjas de tiempo
    nk = int(tiempoLinea/(2*max(tpi)))

    #tiempos max lineas
    Tj = [tiempoLinea]*nj
    for j in range(nj):
        if (j+1) not in lineasDisp:
            Tj[j] = 0

    #tiempos de produccion
    fabriLineas = datos[['L1','L2','L3','L4']]
    tij = fabriLineas.fillna(0).to_numpy()
    Fij = fabriLineas.where(fabriLineas.isnull(), 1).fillna(0)
    Fij = Fij.to_numpy()

    #definicion del modelo
    m = Model(sense=MAXIMIZE)

    #variables
    x = [[[m.add_var(var_type=INTEGER, lb=0) for k in range(nk)] for j in range(nj)] for i in range(ni)]
    y = [[[m.add_var(var_type=BINARY) for k in range(nk)] for j in range(nj)] for i in range(ni)]
    e = [[[m.add_var(var_type=BINARY) for k in range(nk)] for j in range(nj)] for i in range(ni)]
    f = [[[m.add_var(var_type=BINARY) for k in range(nk)] for j in range(nj)] for i in range(ni)]

    #objective function
    m.objective = xsum(x[i][j][k] for i in range(ni) for j in range(nj) for k in range(nk)) - xsum(y[i][j][k] for i in range(ni) for j in range(nj) for k in range(nk)) - xsum(e[i][j][k] for i in range(ni) for j in range(nj) for k in range(nk))

    #restricciones
    for i in range(ni):
        m += xsum(x[i][j][k] for j in range(nj) for k in range(nk)) >= mini[i]

    for i in range(ni):
        m += xsum(x[i][j][k] for j in range(nj) for k in range(nk)) <= maxi[i]

    for j in range(nj):
        for k in range(nk):
            m += xsum((tij[i][j]*x[i][j][k] + tpi[i]*e[i][j][k]) for i in range(ni)) <= Tj[j]/nk

    for k in range(nk):
        m += xsum((y[i][j][k]) for j in range(nj) for i in range(ni)) <= lineasSimultaneas

    for j in range(nj):
        for k in range(nk):
            m += xsum((y[i][j][k]) for i in range(ni)) <= 1

    for i in range(ni):
        for j in range(nj):
            for k in range(nk):
                m += x[i][j][k] - y[i][j][k] >= 0

    for i in range(ni):
        for j in range(nj):
            for k in range(nk):
                m += x[i][j][k] - maxi[i]*y[i][j][k]*Fij[i][j] <= 0

    for i in range(ni):
        for j in range(nj):
            for k in range(nk):
                m += e[i][j][k] <= y[i][j][k]

    for i in range(ni):
        for j in range(nj):
            m += xsum((e[i][j][k]) for k in range(nk)) <= 1

    for i in range(ni):
        for j in range(nj):
            m += xsum((e[i][j][k]) for k in range(nk)) >= xsum(y[i][j][k] for k in range(nk))/nk

    for i in range(ni):
        for j in range(nj):
            for k in range(nk):
                m += f[i][j][k] <= y[i][j][k]

    for i in range(ni):
        for j in range(nj):
            m += xsum((f[i][j][k]) for k in range(nk)) <= 1

    for i in range(ni):
        for j in range(nj):
            m += xsum((f[i][j][k]) for k in range(nk)) >= xsum(y[i][j][k] for k in range(nk))/nk

    for i in range(ni):
        for j in range(nj):
            m += xsum((k*f[i][j][k] - k*e[i][j][k]) for k in range(nk)) >= 0

    for i in range(ni):
        for j in range(nj):
            m += xsum((k*e[i][j][k] + y[i][j][k] - k*f[i][j][k]) for k in range(nk)) == xsum((e[i][j][k]) for k in range(nk))

    for i in range(ni):
        for j in range(nj):
            for (k1, k2) in product(range(nk), range(nk)):
                if k1 != k2:
                    m += k1*y[i][j][k1] <= nk*(1-f[i][j][k2])+k2*f[i][j][k2]

    for i in range(ni):
        for j in range(nj):
            for (k1, k2) in product(range(nk), range(nk)):
                if k1 != k2:
                    m += nk*(1-y[i][j][k1]) + k1*y[i][j][k1] >= k2*e[i][j][k2]
    
    #ejectuar modelo
    m.optimize(max_seconds=240)

    #crear tabla resumen y gantt
    if m.num_solutions:
        tini = inicio
        colores = {}
        ofsCantidades = {'CODART' : datos['CODART'].tolist()}
        ofs = []
        for j in range(nj):
            ofsCantidades['L'+str(j+1)] = []
            for i in range(ni):
                if sum(list(y[i][j][k].x for k in range(nk))) != 0:
                    minIni = round(sum(map(lambda e, k: e*k, list(e[i][j][k].x for k in range(nk)), list(range(nk))))*(Tj[j]/nk))
                    minFin = round(sum(map(lambda f, k: f*(k+1), list(f[i][j][k].x for k in range(nk)), list(range(nk))))*(Tj[j]/nk))
                    inicio = tini + timedelta(minutes=minIni)
                    final = tini + timedelta(minutes=minFin)
                    cantidad = int(sum(list(x[i][j][k].x for k in range(nk))))
                    ofsCantidades['L'+str(j+1)].append(cantidad)
                    dato = str(int(datos['CODART'][i]))
                    ofs.append(dict(Task="Linea"+' '+str(j+1), Start=str(inicio), Finish=str(final), Resource=dato))
                    if dato not in colores:
                        colores[dato] = 'rgb({a},{b},{c})'.format(a=random.randrange(0,255),b=random.randrange(0,255),c=random.randrange(0,255))
                else:
                    ofsCantidades['L'+str(j+1)].append(0)
        fig = ff.create_gantt(ofs,group_tasks=True,index_col='Resource',colors=colores,show_colorbar=False,title='Propuesta de Producción',showgrid_x=True)
        tablaOfs = pd.DataFrame(ofsCantidades)
        tablaOfs['TOTAL'] = tablaOfs.iloc[:,1:].sum(axis=1)
        return dcc.Graph(figure=fig),tablaOfs,colores
    else:
        #si no existe solucion
        return html.H5('No existe una solución. Pruebe con otra selección o cantidades'),None,None
