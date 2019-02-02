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

FOCUSED_ROW = 'row_0'
FOCUSED_ELEMENT = ''
N_ROWS = 3
N_ELEMENTS = 10
# ELTS_PER_ROW = pd.Series(-1, range(N_ROWS))
ELTS_PER_ROW = pd.DataFrame(np.zeros((N_ROWS, N_ELEMENTS), dtype=int))
DISPLAY = {0:{'display':'none'}, 1:{'display':'inline-block'}}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div(className='draggable', id=f'item_{id_row}_{id_item}', style=DISPLAY[ELTS_PER_ROW.loc[id_row, id_item]]) for id_item in range(N_ELEMENTS)
            ], className='row', n_clicks=0, id=f'row_{id_row}', style={'display':'block'}) for id_row in range(N_ROWS)
        ], id='div_maker', className='maker')
    ]),
    html.Button('Add row', id='add_row', n_clicks=0),
    html.Button('Add element', id='add_element', n_clicks=0),
    html.Button('Remove element', id='remove_element', n_clicks=0),
    html.Div(id='dummy'),
    html.Div(id='dummy2')
])

# app.scripts.append_script({"external_url": "C:/Users/renau/App_maker/assets/interactjs/dist/interact.min.js"})
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
                 [Input('dummy2', 'data-dummy')])
    def f(focused):
        global ELTS_PER_ROW
        global FOCUSED_ROW
        global FOCUSED_ELEMENT
        row = int(id.split('_')[1])
        elt = int(id.split('_')[2])
        if id == focused:
            return {'display':'inline-block', 'background-color':'rgba(0,200,0,.25)'}
        elif ELTS_PER_ROW.loc[row, elt] == 1:
            return {'display':'inline-block'}
        else:
            return{'display':'none'}

    return app

@app.callback(Output('dummy', 'data-dummy'),
             [Input(f'row_{i}', 'n_clicks_timestamp') for i in range(N_ROWS)])
def f(*args):
    global FOCUSED_ROW
    s = pd.Series(args, index=[f'row_{i}' for i in range(N_ROWS)])
    if not s.dropna().empty:
        FOCUSED_ROW = s.idxmax()
    return FOCUSED_ROW


@app.callback(Output('dummy2', 'data-dummy'),
             [Input('add_element', 'n_clicks_timestamp'),
              Input('remove_element', 'n_clicks_timestamp')] +
             [Input(f'item_{i}_{j}', 'n_clicks_timestamp') for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
def f(ts_add, ts_rmv, *args):
    global FOCUSED_ELEMENT
    global FOCUSED_ROW
    global ELTS_PER_ROW
    s = pd.Series(args, index=[f'item_{i}_{j}' for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
    s['add'] = ts_add
    s['rmv'] = ts_rmv
    s = s.astype(float)
    focused_before = FOCUSED_ELEMENT
    if not s.dropna().empty:
        FOCUSED_ELEMENT = s.dropna().idxmax()
        row = int(FOCUSED_ROW.split('_')[1])
        if FOCUSED_ELEMENT == 'add':
            elt = ELTS_PER_ROW.loc[row][ELTS_PER_ROW.loc[row] == 0].index.min()
            ELTS_PER_ROW.at[row, elt] = 1
            FOCUSED_ELEMENT = f'item_{row}_{elt}'
        elif FOCUSED_ELEMENT == 'rmv':
            row_before = int(focused_before.split('_')[1])
            elt_before = int(focused_before.split('_')[2])
            ELTS_PER_ROW.at[row_before, elt_before] = 0
            elt = ELTS_PER_ROW.loc[row][ELTS_PER_ROW.loc[row] == 1].index.max()
            FOCUSED_ELEMENT = f'item_{row}_{elt}'

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



for id_row in range(N_ROWS):
    app = add_row_click_callback(app, f'row_{id_row}')
    app = add_row_focus_callback(app, f'row_{id_row}')
    for id_elt in range(N_ELEMENTS):
        app = add_element_style_callback(app, f'item_{id_row}_{id_elt}')


if __name__ == '__main__':
    app.run_server(debug=False)

