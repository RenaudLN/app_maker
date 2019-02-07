import datetime
import time
import numpy as np
import pandas as pd
import itertools

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dtt
import plotly.graph_objs as go
import plotly.offline as py
from dash.dependencies import Input, Output, State

import var

FOCUSED_ROW = 'row_0'
FOCUSED_ELEMENT = 'item_0_0'
N_ROWS = 6
N_ELEMENTS = 12
ELTS_PER_ROW = pd.DataFrame(np.zeros((N_ROWS, N_ELEMENTS), dtype=int))
ELTS_PER_ROW.at[0, 0] = 1
ACTIVE_ROWS = pd.Series({i:0 for i in range(N_ROWS)})
ELT_PROPS = {f'item_{i}_{j}':pd.DataFrame([['type', 'div']] + [[prop, ''] for prop in var.component_properties['div']], columns=['Property', 'Value'])
                for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div(className='elt hidden', id=f'item_{id_row}_{id_item}') for id_item in range(N_ELEMENTS)
                    ], className='line hidden', n_clicks=0, id=f'row_{id_row}') for id_row in range(N_ROWS)
                ], id='div_maker', className='maker'
            ),
        ], style={'display':'table-cell'}),
            
        html.Div([html.Button('Add row', id='add_row', n_clicks=0), html.Br(),
                html.Button('Add element', id='add_element', n_clicks=0), html.Br(),
                html.Button('Remove element', id='remove_element', n_clicks=0), html.Br(),
                html.Button('Reset', id='reset', n_clicks=0), html.Br(),
            ], id='div_btns'
        ),
        html.Div([
            dtt.DataTable(id='elt_info', 
                columns=[{'name':'Property', 'id':'Property', 'editable':False}, {'name':'Value', 'id':'Value', 'editable':True}],
                data=ELT_PROPS[FOCUSED_ELEMENT].to_dict('rows'),
                editable=True,
            )
        ], id='div_controls')
    ], style={'display':'table'}),
    
    html.Div(id='dummy'),
    html.Div(id='dummy2'),
    html.Div(id='dummy3'),
    html.Div(id='dummy4'),
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

    @app.callback(Output(id, 'className'),
                 [Input('dummy', 'data-dummy'),
                  Input('dummy3', 'data-dummy')])
    def f(data, trigger):
        global ACTIVE_ROWS
        row = int(id.split('_')[1])
        if ACTIVE_ROWS[row] == 1:
            if data is not None and data == id:
                return 'line focused'
            else:
                return 'line'
        else:
            return 'line hidden'
    
    return app

def add_element_style_callback(app, id):

    @app.callback(Output(id, 'className'),
                 [Input('dummy2', 'data-dummy')])
    def f(focused):
        global ELTS_PER_ROW
        global FOCUSED_ROW
        global FOCUSED_ELEMENT
        row = int(id.split('_')[1])
        elt = int(id.split('_')[2])
        if id == focused:
            return 'elt focused'
            return {'display':'inline-block', 'background-color':'rgba(180, 180, 180, .25)',
                    'box-shadow': '0 1px 1px rgba(0, 0, 0, 0.075) inset, 0 0 8px rgba(58, 72, 224, 0.9)'}
        elif ELTS_PER_ROW.loc[row, elt] == 1:
            return 'elt'
            return {'display':'inline-block'}
        else:
            return 'elt hidden'
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

@app.callback(Output('elt_info', 'data'),
             [Input('elt_info', 'data_timestamp'),
              Input('add_element', 'n_clicks_timestamp'),
              Input('remove_element', 'n_clicks_timestamp')] +
             [Input(f'item_{i}_{j}', 'n_clicks_timestamp') for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))],
             [State('elt_info', 'data')])
def update_id(ts_data, ts_add, ts_rmv, *args):
    time.sleep(.2)
    global ELT_PROPS
    global FOCUSED_ELEMENT
    s = pd.Series(args[:-1], index=[f'item_{i}_{j}' for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
    s['data'] = ts_data
    s['add'] = ts_add
    s['rmv'] = ts_rmv
    s = s.astype(float)
    if not s.dropna().empty and s.dropna().idxmax() == 'data':
        data = pd.DataFrame(args[-1])
        component = data.loc[data.Property == 'type'].Value.values[0].lower()
        print('COMPONENT', component)
        if component in var.component_properties.keys():
            print('HERE')
            new_data = pd.DataFrame([{'Property':'type', 'Value':component}] + 
                                    [{'Property':p, 'Value':''} for p in var.component_properties[component]])
            for prop in data.Property.values:
                if prop in new_data.Property.values:
                    new_data.at[new_data.loc[new_data.Property == prop].index[0], 'Value'] = data.loc[data.Property==prop].Value.values[0]
            ELT_PROPS[FOCUSED_ELEMENT] = new_data
            return new_data.to_dict('rows')
    data = ELT_PROPS[FOCUSED_ELEMENT]
    data.at[data.loc[data.Property == 'id'].index[0], 'Value'] = FOCUSED_ELEMENT if data.at[data.loc[data.Property == 'id'].index[0], 'Value'] == '' else data.at[data.loc[data.Property == 'id'].index[0], 'Value']
    return ELT_PROPS[FOCUSED_ELEMENT].to_dict('rows')

for id_row in range(N_ROWS):
    app = add_row_click_callback(app, f'row_{id_row}')
    app = add_row_focus_callback(app, f'row_{id_row}')
    for id_elt in range(N_ELEMENTS):
        app = add_element_style_callback(app, f'item_{id_row}_{id_elt}')

# @app.callback(Output('dummy4', 'data-dummy'),
#              [Input('elt_info', 'data')])
# def update_elt_info(data):
#     global ELT_PROPS
#     global FOCUSED_ELEMENT
#     ELT_PROPS[FOCUSED_ELEMENT] = pd.DataFrame(data)
#     return ''

if __name__ == '__main__':
    app.run_server(debug=False)

