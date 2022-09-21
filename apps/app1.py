import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd

from app import app
from calculos import vistaPropuestas, generarTabla, generarPropuesta

layout = html.Div([
    dbc.Container([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.FormGroup(
                    [
                        dbc.Label('Líneas Disponibles'),
                        dbc.Col(
                            dbc.Checklist(
                                persistence = True,
                                persistence_type = 'memory',
                                id = 'lineasDisponibles',
                                options = [
                                    {"label": "L1", "value": 1},
                                    {"label": "L2", "value": 2},
                                    {"label": "L3", "value": 3},
                                    {"label": "L4", "value": 4}
                                ],
                                value = [1,2,3,4],
                                switch=True
                            ),
                        )      
                    ],
                    row="True"
                    )
                ]),
                dbc.Row([
                    dbc.FormGroup(
                    [
                        dbc.Label('Líneas Simultáneas'),
                        dbc.Col(
                            dbc.Input(id = 'numLineasSim', type="number", min=1, max=4, step=1, value=3, persistence = True,persistence_type = 'memory',)
                        )
                    ],
                    row = True
                    )
                ]),
                dbc.Row([
                    dbc.FormGroup(
                    [
                        dbc.Label('Hora Inicio'),
                        dbc.Col(
                            dbc.Input(id = 'horaInicio', type="time", value="08:00",persistence = True,persistence_type = 'memory',)
                        )
                    ],
                    row = True
                    )
                ]),
                dbc.Row([
                    dbc.FormGroup(
                    [
                        dbc.Label('Hora Fin'),
                        dbc.Col(
                            dbc.Input(id = 'horaFin', type="time", value="19:00",persistence = True,persistence_type = 'memory',)
                        )
                    ],
                    row = True
                    )
                ]),
                dbc.Row([
                    dbc.Button("Ver Tabla", id='botonTabla',color="primary", className="mr-1"),
                    dbc.Button("Generar Propuesta", id='botonGenerar',color="success", className="mr-1")
                ])
            ], width = 2),
            dbc.Col([
                dash_table.DataTable(
                    id = 'vistaDatos',
                    persistence = True,
                    persistence_type = 'memory',
                    persisted_props = ['data','selected_rows'],
                    columns = [
                        {"name": 'Artículo', "id": 'CODART'},
                        {"name": 'Descripción', "id": 'DESCART'},
                        {"name": 'Stock Mínimo', "id": 'STOCKMIN'},
                        {"name": 'Stock Actual', "id": 'STOCKALM'},
                        {"name": 'Pedidos', "id": 'PEDIDOS'},
                        {"name": 'Propuesta', "id": 'PROPUESTA'},
                        {"name": 'Producir', "id": 'PRODUCIR', 'editable': True, 'type': 'numeric'}
                    ],
                    data = vistaPropuestas().to_dict('records'),
                    fixed_rows={'headers': True},
                    style_table={'height': 450},
                    row_selectable="multi",
                    selected_rows=[],
                    style_header={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': ['CODART','STOCKMIN','STOCKALM','PEDIDOS']},
                        'width': '8%'},
                        {'if': {'column_id': ['PROPUESTA','PRODUCIR']},
                        'width': '9%'},
                        {'if': {'column_id': 'DESCART'},
                        'width': '50%'},
                    ],
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{STOCKALM} < {PEDIDOS}',
                                'column_id': 'CODART'
                            },
                            'color': 'tomato',
                            'fontWeight': 'bold'

                        },
                        {
                            'if': {
                                'column_id': 'PRODUCIR'
                            },
                            'backgroundColor': 'rgba(192, 255, 153)',
                            'fontWeight': 'bold'
                            
                        }
                    ],
                ),
                dcc.Store(id='memoriaTabla',storage_type='memory')
            ],width = 10)
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Div(dbc.Alert('Selecciona algún Artículo!',id='alertaNoSeleccion',is_open=False)),
                dbc.Spinner(html.Div(id = 'graficoGantt'))
            ], width = 9),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id = 'colTablaOfs')
                    ]),
                ]),
                dbc.Row([
                    dbc.Col(
                        id = 'botonPlanta',
                        align='center'
                    )
                ],style={"height": "100px"})
            ],width = 3)
        ],form=True,align='center'),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                id = 'colTabla'
            )
        ])
    ]) 
])


@app.callback(Output('colTabla', 'children'),
    [Input('botonTabla', 'n_clicks')],
    [
        State('lineasDisponibles', 'value'),
        State('numLineasSim', 'value'),
        State('horaInicio', 'value'),
        State('horaFin', 'value'),
        State('vistaDatos', 'derived_virtual_selected_rows'),
        State('memoriaTabla','data')
    ]
)
def tabla(n_clicks,lineasDisponibles,numLineasSim,horaInicio,horaFin,vistaDatos,data):
    if n_clicks != None:
        tablaEditada = pd.DataFrame.from_records(data)
        df = generarTabla(lineasDisponibles,numLineasSim,horaInicio,horaFin,vistaDatos,tablaEditada)
        return dbc.Table.from_dataframe(df,id ='tabla',striped=True, bordered=True, hover=True)


@app.callback(Output('memoriaTabla', 'data'),
    [Input('vistaDatos', 'data')]
)
def guardarTabla(data):
    return data


def generaTablaOfs(tabla,colores):
    tablaOfs = dash_table.DataTable(
        id= 'tablaOfs',
        data=tabla.to_dict('records'),
        columns= [
            {"name": 'Artículo', "id": 'CODART'},
            {"name": 'L1', "id": 'L1'},
            {"name": 'L2', "id": 'L2'},
            {"name": 'L3', "id": 'L3'},
            {"name": 'L4', "id": 'L4'},
            {"name": 'Total', "id": 'TOTAL'},
        ],
        style_data_conditional=([
        {
            'if': {
                'filter_query': '{{CODART}} = {}'.format(codart),
                'column_id': 'CODART'
            },
            'backgroundColor': colores[codart],
            'color': 'white'
        } for codart in colores]),
    )
    return tablaOfs


@app.callback(
    [Output('alertaNoSeleccion', 'is_open'),
    Output('graficoGantt', 'children'),
    Output('colTablaOfs', 'children'),
    Output('botonPlanta', 'children'),
    ],
    [Input('botonGenerar', 'n_clicks')],
    [
        State('lineasDisponibles', 'value'),
        State('numLineasSim', 'value'),
        State('horaInicio', 'value'),
        State('horaFin', 'value'),
        State('vistaDatos', 'derived_virtual_selected_rows'),
        State('memoriaTabla','data')
    ]
)
def generarGantt(n_clicks,lineasDisponibles,numLineasSim,horaInicio,horaFin,vistaDatos,data):
    if n_clicks != None:
        tablaEditada = pd.DataFrame.from_records(data)
        if len(vistaDatos) == 0:
            return True,None,None,None
        else:
            gantt,tabla,colores = generarPropuesta(lineasDisponibles,numLineasSim,horaInicio,horaFin,vistaDatos,tablaEditada)
            if colores == None:
                return False,gantt,None,None
            else:
                return False,gantt,generaTablaOfs(tabla,colores),dbc.Button('Enviar a Planta', id='botonEnviarPlanta',color="success")
    else:
        return False,None,None,None