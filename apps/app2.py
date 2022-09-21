import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd

from app import app

def tablaProdFamilias():
    df = pd.read_csv('assets/prodFamilias.csv',sep=';')
    return dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data = df.to_dict('records'),
                fixed_rows={'headers': True},
                style_table={'height': 450},
                style_header={
                },
                style_cell_conditional=[
                ],
                style_data_conditional=[
                ],
            )
def tablaProdSubfamilias():
    df = pd.read_csv('assets/prodSubfamilias.csv',sep=';')
    return dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data = df.to_dict('records'),
                fixed_rows={'headers': True},
                style_table={'height': 450},
                style_header={
                },
                style_cell_conditional=[
                ],
                style_data_conditional=[
                ],
            )
def familias():
    df = pd.read_csv('assets/familias.csv',sep=';')
    return [{"label": i, "value": i} for i in list(dict.fromkeys(df['FAMILIA'].tolist()))]
def subfamilias():
    df = pd.read_csv('assets/familias.csv',sep=';')
    return [{"label": i, "value": i} for i in list(dict.fromkeys(df['SUBFAMILIA'].tolist()))]

layout = html.Div([
    dbc.Container([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Artículo", className="mr-1"),
                        dbc.Input(type="number", placeholder="CODART"),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("L1", className="mr-2"),
                        dbc.Select(
                            options=[
                                {"label": "True", "value": True},
                                {"label": "False", "value": False},
                            ],
                        ),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("L2", className="mr-2"),
                        dbc.Select(
                            options=[
                                {"label": "True", "value": True},
                                {"label": "False", "value": False},
                            ],
                        ),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("L3", className="mr-2"),
                        dbc.Select(
                            options=[
                                {"label": "True", "value": True},
                                {"label": "False", "value": False},
                            ],
                        ),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("L4", className="mr-2"),
                        dbc.Select(
                            options=[
                                {"label": "True", "value": True},
                                {"label": "False", "value": False},
                            ],
                        ),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Tiempo SubFamilia", className="mr-2"),
                        dbc.Select(
                            options=[
                                {"label": "True", "value": True},
                                {"label": "False", "value": False},
                            ],
                        ),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.Button("Actualizar Datos", color="danger"),
            ],align='center'),
        ],form=True),
        dbc.Row([
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Producción Mínima", className="mr-1"),
                        dbc.Input(type="number", placeholder="unidades"),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Tiempo Producción", className="mr-1"),
                        dbc.Input(type="number", placeholder="min/unidad"),
                    ],
                ),
            ]),
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Tiempo Preparación", className="mr-1"),
                        dbc.Input(type="number", placeholder="minutos"),
                    ],
                ),
            ]),
        ],form = True),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Buscar Artículo", className="mr-1"),
                        dbc.Input(type="number", id='buscarCodart', placeholder="CODART"),
                        dbc.Button("Buscar", id = 'botonBuscar', color="success"),
                        dbc.Button("Reset", id = 'resetBuscar', color="primary"),
                    ],
                ),
            ],width=2, align = 'center'),
            dbc.Col(dbc.Spinner(html.Div(id = 'vistaDatos')),width=10)
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.FormGroup(
                    [
                        dbc.Label("Subfamilia", className="mr-1"),
                        dbc.Select(options = subfamilias()),
                        dbc.Label("Tiempo Producción", className="mr-1"),
                        dbc.Input(type="number", placeholder="Tiempo"),
                        dbc.Button("Actualizar Datos", color="danger"),
                    ],
                ),
            ],width=2, align = 'center'),
            dbc.Col(children=tablaProdSubfamilias(),id='tablaProdSubfamilias',width=10)
        ]),
        html.Hr(),
    ]) 
])

def tablaProdArticulos(df):
    return dash_table.DataTable(
                columns = [
                    {"name": 'Artículo', "id": 'CODART'},
                    {"name": 'L1', "id": 'L1'},
                    {"name": 'L2', "id": 'L2'},
                    {"name": 'L3', "id": 'L3'},
                    {"name": 'L4', "id": 'L4'},
                    {"name": 'Cantidad Mínima', "id": 'PRODMIN'},
                    {"name": 'Tiempo SubFamilia', "id": 'PRODFAM'},
                    {"name": 'Tiempo Producción', "id": 'TPROD'},
                    {"name": 'Tiempo Preparar', "id": 'TPREP'}
                ],
                data = df.to_dict('records'),
                fixed_rows={'headers': True},
                style_table={'height': 450},
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_cell_conditional=[
                    {'if': {'column_id': ['L1','L2','L3','L4']},
                    'width': '7%'},
                    {'if': {'column_id': 'CODART'},
                    'width': '8%'},
                    {'if': {'column_id': ['PRODMIN','PRODFAM','TPROD','TPREP']},
                    'width': '16%'},
                ],
            )


@app.callback(Output('vistaDatos', 'children'),
    [
        Input('botonBuscar', 'n_clicks'),
        Input('resetBuscar', 'n_clicks'),
    ],
    [
        State('buscarCodart', 'value')
    ]
)
def filtroVista(boton1, boton2, buscarCodart):
    df = pd.read_csv('assets/prodArticulos.csv',sep=',')
    ctx = dash.callback_context
    if not ctx.triggered:
        return tablaProdArticulos(df)
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'botonBuscar':
        return tablaProdArticulos(df[df['CODART']==buscarCodart])
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'resetBuscar':
        return tablaProdArticulos(df)

