import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=['assets/bootstrap.css'])
server = app.server
app.title = 'Producción Salim'