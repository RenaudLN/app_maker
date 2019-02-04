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
N_ROWS = 6
N_ELEMENTS = 12
# ELTS_PER_ROW = pd.Series(-1, range(N_ROWS))
ELTS_PER_ROW = pd.DataFrame(np.zeros((N_ROWS, N_ELEMENTS), dtype=int))
DISPLAY = {0:{'display':'none'}, 1:{'display':'inline-block'}}
ACTIVE_ROWS = pd.Series({i:0 for i in range(N_ROWS)})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div(className='draggable', id=f'item_{id_row}_{id_item}', style=DISPLAY[ELTS_PER_ROW.loc[id_row, id_item]]) for id_item in range(N_ELEMENTS)
                ], className='row', n_clicks=0, id=f'row_{id_row}', style=DISPLAY[ACTIVE_ROWS[id_row]]) for id_row in range(N_ROWS)
            ], id='div_maker', className='maker'
        ),
        html.Div([html.Button('Add row', id='add_row', n_clicks=0), html.Br(),
                html.Button('Add element', id='add_element', n_clicks=0), html.Br(),
                html.Button('Remove element', id='remove_element', n_clicks=0), html.Br(),
                html.Button('Reset', id='reset', n_clicks=0), html.Br(),
            ], id='div_btns', className='buttons'
        )
    ], style={'display':'table'}),
    
    html.Div(id='dummy'),
    html.Div(id='dummy2'),
    html.Div(id='dummy3'),
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
                 [Input('dummy', 'data-dummy'),
                  Input('dummy3', 'data-dummy')])
    def f(data, trigger):
        global ACTIVE_ROWS
        row = int(id.split('_')[1])
        if ACTIVE_ROWS[row] == 1:
            if data is not None and data == id:
                return{'box-shadow': '0 1px 1px rgba(0, 0, 0, 0.075) inset, 0 0 8px rgba(239, 102, 104, 0.9)'}
                return {'border':'1px solid red'}
            else:
                return {}
        else:
            return {'display':'none'}
    
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
            return {'display':'inline-block', 'background-color':'rgba(180, 180, 180, .25)',
                    'box-shadow': '0 1px 1px rgba(0, 0, 0, 0.075) inset, 0 0 8px rgba(58, 72, 224, 0.9)'}
        elif ELTS_PER_ROW.loc[row, elt] == 1:
            return {'display':'inline-block'}
        else:
            return{'display':'none'}

    return app

@app.callback(Output('dummy', 'data-dummy'),
             [Input('add_row', 'n_clicks_timestamp')] +
             [Input(f'row_{i}', 'n_clicks_timestamp') for i in range(N_ROWS)])
def f(ts_add, *args):
    global FOCUSED_ROW
    global ACTIVE_ROWS
    s = pd.Series(args, index=[f'row_{i}' for i in range(N_ROWS)])
    s['add'] = 0 if ts_add is None else ts_add
    s = s.astype(float)
    if not s.dropna().empty:
        FOCUSED_ROW = s.idxmax()
        if FOCUSED_ROW == 'add':
            FOCUSED_ROW = 'row_{}'.format(ACTIVE_ROWS[ACTIVE_ROWS == 1].index.max())
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

@app.callback(Output('dummy3', 'data-dummy'),
             [Input('add_row', 'n_clicks_timestamp'),
              Input('reset', 'n_clicks_timestamp')])
def f(ts_add, ts_rst):
    global ACTIVE_ROWS
    ts_add = 0 if ts_add is None else ts_add
    ts_rst = 0 if ts_rst is None else ts_rst
    if ts_add >= ts_rst:
        row = ACTIVE_ROWS[ACTIVE_ROWS == 0].index.min()
        ACTIVE_ROWS[row] = 1
        return row
    else:
        ACTIVE_ROWS = pd.Series(0, ACTIVE_ROWS.index)
        ACTIVE_ROWS[0] = 1
        return 0



for id_row in range(N_ROWS):
    app = add_row_click_callback(app, f'row_{id_row}')
    app = add_row_focus_callback(app, f'row_{id_row}')
    for id_elt in range(N_ELEMENTS):
        app = add_element_style_callback(app, f'item_{id_row}_{id_elt}')


if __name__ == '__main__':
    app.run_server(debug=False)

