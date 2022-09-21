import pandas as pd
from datetime import datetime
import numpy as np
from programaLineal import optimiza

def vistaPropuestas():
    df = pd.read_csv('assets/generacionofs.csv',sep=',')
    prodArticulos = pd.read_csv('assets/prodArticulos.csv', sep = ',', usecols=['CODART','PRODMIN'])
    datos = pd.merge(left=df,right=prodArticulos,left_on='CODART',right_on='CODART')
    datos['PRODUCIR'] = datos[['PROPUESTA', 'PRODMIN']].max(axis=1)
    datos = datos.sort_values('PEDIDOS', ascending = False)
    return datos

def tiempos(codart,linia,datos):
    prodSubfamilias = pd.read_csv('assets/prodSubfamilias.csv',sep=';')
    if datos[datos['CODART'] == codart]['L{}'.format(linia)].values[0] == False:
        return np.nan
    else:
        if datos[datos['CODART'] == codart]['PRODFAM'].values[0] == True:
            return prodSubfamilias[prodSubfamilias['SUBFAMILIA']==datos[datos['CODART'] == codart]['SUBFAMILIA'].values[0]]['TPROD'].values[0]
        else:
            datos[datos['CODART'] == codart]['TPROD'].values[0]

def generarTabla(lineasDisp,lineasSimultaneas,horaIni,horaFin,seleccion,tablaEditada):
    articulosProd = tablaEditada.iloc[seleccion]

    prodArticulos = pd.read_csv('assets/prodArticulos.csv', sep = ',')
    familias = pd.read_csv('assets/familias.csv',sep=';')

    articulosProd = articulosProd[['CODART','PRODUCIR','STOCKMIN']]

    datos = pd.merge(left=articulosProd,right=prodArticulos,left_on='CODART',right_on='CODART')
    datos = pd.merge(left=datos,right=familias,left_on='CODART',right_on='CODART')
    datos['PRODMIN'] = datos[['PRODMIN', 'PRODUCIR']].max(axis=1)

    #prod max = prodmin + stockmin (mas o menos como stockmin x2)
    datos['PRODMAX'] = datos['PRODMIN'] + datos['STOCKMIN']

    for i in range(4):
        linia = i+1
        datos['L{}'.format(linia)] = datos['CODART'].apply(lambda codart: tiempos(codart,linia,datos))

    datos = datos[['CODART','L1','L2','L3','L4','PRODMIN','PRODMAX','TPREP']]

    return datos.astype('float')

def generarPropuesta(lineasDisp,lineasSimultaneas,horaIni,horaFin,seleccion,tablaEditada):
    datos = generarTabla(lineasDisp,lineasSimultaneas,horaIni,horaFin,seleccion,tablaEditada)
    return optimiza(datos,horaIni,horaFin,lineasSimultaneas,lineasDisp)