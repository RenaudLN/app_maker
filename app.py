import datetime
import time
import numpy as np
import pandas as pd
import itertools

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.offline as py
from dash.dependencies import Input, Output, State

# import callbacks

FOCUSED_ROW = 'row_0'
FOCUSED_ELEMENT = ''
N_ROWS = 3
N_ELEMENTS = 10
ELTS_PER_ROW = pd.Series(-1, range(N_ROWS))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # dcc.Interval(id='update_focus', interval=1000, n_intervals=0),
    html.Div([
        # html.H4('App Maker'),
        html.Div([
            html.Div([
                html.Div(className='draggable', id=f'item_{id_row}_{id_item}', style={'display':'none'}) for id_item in range(N_ELEMENTS)
            ], className='row', n_clicks=0, id=f'row_{id_row}', style={'display':'block'}) for id_row in range(N_ROWS)
        ], id='div_maker', className='maker')
    ]),
    html.Button('Add row', id='add_row', n_clicks=0),
    html.Button('Add element', id='add_element', n_clicks=0),
    html.Button('Remove element', id='remove_element', n_clicks=0),
    html.Div(id='dummy'),
    html.Div(id='dummy2')
])

app.scripts.append_script({"external_url": "http://code.interactjs.io/v1.3.4/interact.min.js"})

def add_row_click_callback(app, id):

    @app.callback(Output(id, 'data-dummy'),
                 [Input(id, 'n_clicks')])
    def f(n):
        if n > 0:
            global FOCUSED_ROW
            FOCUSED_ROW = id
            return ''

    return app

def add_row_focus_callback(app, id):

    @app.callback(Output(id, 'style'),
                 [Input('dummy', 'data-dummy')])
    def f(data):
        if data is not None and data == id:
            return {'border':'1px solid red'}
        else:
            return {}
    
    return app

def add_elt_focus_callback(app, id):

    @app.callback(Output(id, 'data-dummy'),
                 [Input('dummy', 'data-dummy')])
    def f(data):
        if data is not None and data == id:
            return {'border':'1px solid red'}
        else:
            return {}
    
    return app

def add_element_style_callback(app, id):

    @app.callback(Output(id, 'style'),
                 [Input('add_element', 'n_clicks_timestamp'),
                  Input('remove_element', 'n_clicks_timestamp')],
                 [State(id, 'style'),
                  State('dummy2', 'data-dummy')])
    def f(ts_add, ts_rmv, style, data):
        global ELTS_PER_ROW
        global FOCUSED_ROW
        row_number = int(FOCUSED_ROW.split('_')[-1])
        row = int(id.split('_')[1])
        elt = int(id.split('_')[2])
        if ts_add is None:
            ts_add = 0
        if ts_rmv is None:
            ts_rmv = 0
        if ts_add > ts_rmv:
            if row == row_number and elt == ELTS_PER_ROW[row_number] + 1:
                ELTS_PER_ROW[row_number] = ELTS_PER_ROW[row_number] + 1
                return {'display':'inline-block'}
        elif ts_add < ts_rmv:
            if id == data:
                ELTS_PER_ROW[row_number] = ELTS_PER_ROW[row_number] - 1
                return {'display':'none'}
        return style


    return app

@app.callback(Output('dummy', 'data-dummy'),
             [Input(f'row_{i}', 'n_clicks') for i in range(N_ROWS)])
def f(*args):
    # if np.any(np.array(args) > 0):
    global FOCUSED_ROW
    return FOCUSED_ROW

@app.callback(Output('dummy2', 'data-dummy'),
             [Input(f'item_{i}_{j}', 'n_clicks_timestamp') for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
def f(*args):
    s = pd.Series(args, index=[f'item_{i}_{j}' for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
    if not s.dropna().empty:
        global FOCUSED_ELEMENT
        FOCUSED_ELEMENT = s.idxmax()
        return FOCUSED_ELEMENT

# @app.callback(Output('div_maker', 'children'),
#              [Input('add_row', 'n_clicks')],
#              [State('div_maker', 'children')])
# def f(n, children):
#     global app
#     if n is None:
#         n = 0
#     row = html.Div(className='row', n_clicks=0, id='row_{}'.format(n))
#     if children is None:
#         out = [row]
#     else:
#         out = children + [row]
#     app.layout.children[0].children[0].children.append(row)
#     app = add_row_click_callback(app, 'row_{}'.format(n))
#     print(app.callback_map)
#     return out

# @app.callback(Output('add_element', 'data-dummy'),
#              [Input('add_element', 'n_clicks')])
# def f(n):
#     if n > 0:
#         print('FOCUSED_ROW:', FOCUSED_ROW)


for id_row in range(N_ROWS):
    app = add_row_click_callback(app, f'row_{id_row}')
    app = add_row_focus_callback(app, f'row_{id_row}')
    for id_elt in range(N_ELEMENTS):
        app = add_element_style_callback(app, f'item_{id_row}_{id_elt}')


if __name__ == '__main__':
    app.run_server(debug=True)

