import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2

#barra de navegación
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Propuesta OF's", href='/apps/app1')),
        dbc.NavItem(dbc.NavLink("Datos Producción", href='/apps/app2')),
    ],
    brand="Producción Salim",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return app1.layout
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)