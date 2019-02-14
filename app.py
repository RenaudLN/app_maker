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
N_ROWS = 3
N_ELEMENTS = 4
ELTS_PER_ROW = pd.DataFrame(np.zeros((N_ROWS, N_ELEMENTS), dtype=int))
ELTS_PER_ROW.at[0, 0] = 1
ACTIVE_ROWS = pd.Series({i:0 for i in range(N_ROWS)})
default_component = 'Div'
ELT_PROPS = {f'item_{i}_{j}':pd.DataFrame([['Component', default_component]] +
                                          [[prop, ''] for prop in var.component_properties[default_component]],
                                          columns=['Property', 'Value'])
            for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))}
ELT_WIDTH = pd.Series(150, index=[f'item_{i}_{j}' for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
DX = 50

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title = 'App maker'

app.layout = html.Div([
    dcc.Tabs([dcc.Tab(label='Maker', value='maker'),
              dcc.Tab(label='Viewer', value='viewer')],
             value='maker', id='tabs'),
    html.Div(id='tabs_content')
])

maker = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                            html.Div('-', id=f'minus_{id_row}_{id_item}', className='width_control minus'),
                            html.Div('+', id=f'plus_{id_row}_{id_item}', className='width_control plus'),
                        ], className='elt hidden row', id=f'item_{id_row}_{id_item}',
                        style={'width':'{}px'.format(ELT_WIDTH[f'item_{id_row}_{id_item}'])}) for id_item in range(N_ELEMENTS)
                    ], className='line hidden', n_clicks=0, id=f'row_{id_row}') for id_row in range(N_ROWS)
                ], id='div_maker', className='maker'
            ),
        ], style={'display':'table-cell'}),
            
        html.Div([html.Button('Add row', id='add_row', className='elt_control', n_clicks=0), html.Br(),
                html.Button('Add element', id='add_element', className='elt_control', n_clicks=0), html.Br(),
                html.Button('Remove element', id='remove_element', className='elt_control', n_clicks=0), html.Br(),
                html.Button('Reset', id='reset', className='elt_control', n_clicks=0), html.Br(),
            ], id='div_btns'
        ),
        html.Div([
            dtt.DataTable(id='elt_info', 
                columns=[{'name':'Property', 'id':'Property', 'editable':False}, {'name':'Value', 'id':'Value', 'editable':True}],
                data=ELT_PROPS[FOCUSED_ELEMENT].to_dict('rows'),
                editable=True,
            )
        ], id='div_controls')
    ], style={'display':'table'}, id='blabla'),
    
    html.Div(id='dummy')
])

def render_viewer():
    children = []
    for i_row in ACTIVE_ROWS[ACTIVE_ROWS==1].index:
        r = ELTS_PER_ROW.loc[i_row]
        c_list = []
        for i_elt in r[r==1].index:
            element = pd.DataFrame(ELT_PROPS[f'item_{int(i_row)}_{int(i_elt)}'])
            component = element[element.Property == 'Component'].Value.values[0].capitalize()
            element = element[element.Property != 'Component'].set_index('Property').Value
            kwargs = element[element != ''].to_dict()
            if component in dir(dcc):
                lib = 'dcc'
            else:
                lib = 'html'
            c_list.append(eval(f'{lib}.{component}(**kwargs)'))
        children.append(html.Div(children=c_list, className='row'))
    viewer = html.Div(children=children, id='viewer')
    return viewer

# app.scripts.append_script({"external_url": "http://code.interactjs.io/v1.3.4/interact.min.js"})

@app.callback(Output('tabs_content', 'children'),
             [Input('tabs', 'value')])
def update_tab(tab):
    if tab == 'maker':
        return maker
    elif tab == 'viewer':
        viewer = render_viewer()
        return viewer


def add_row_click_callback(app, id):

    @app.callback(Output(id, 'data-none'),
                 [Input(id, 'n_clicks')])
    def f(n):
        if n > 0:
            global FOCUSED_ROW
            FOCUSED_ROW = id
            return ''

    return app

def add_row_focus_callback(app, id):

    @app.callback(Output(id, 'className'),
                 [Input('dummy', 'data-row'),
                  Input('dummy', 'data-focused_row')])
    def f(*triggers):
        global ACTIVE_ROWS
        global FOCUSED_ROW
        row = int(id.split('_')[1])
        if ACTIVE_ROWS[row] == 1:
            if FOCUSED_ROW is not None and FOCUSED_ROW == id:
                return 'line focused'
            else:
                return 'line'
        else:
            return 'line hidden'
    
    return app

def add_element_class_callback(app, id):

    @app.callback(Output(id, 'className'),
                 [Input('dummy', 'data-focused_elt')])
    def f(focused):
        global ELTS_PER_ROW
        global FOCUSED_ROW
        global FOCUSED_ELEMENT
        row = int(id.split('_')[1])
        elt = int(id.split('_')[2])
        if id == focused:
            return 'elt focused'
        elif ELTS_PER_ROW.loc[row, elt] == 1:
            return 'elt'
        else:
            return 'elt hidden'

    return app

def add_element_style_callback(app, id):

    minus_div = 'minus_' + '_'.join(id.split('_')[1:])
    plus_div = 'plus_' + '_'.join(id.split('_')[1:])

    @app.callback(Output(id, 'style'),
                 [Input(minus_div, 'n_clicks_timestamp'),
                  Input(plus_div, 'n_clicks_timestamp')])
    def update_width(ts_minus, ts_plus):
        global ELT_WIDTH
        ts_minus = 0 if ts_minus is None else ts_minus
        ts_plus = 0 if ts_plus is None else ts_plus
        current_width = ELT_WIDTH[id]
        if ts_plus > ts_minus:
            width = min(current_width + DX, 600)
        elif ts_minus > ts_plus:
            width = max(current_width - DX, 50)
        else:
            width = current_width
        ELT_WIDTH[id] = width
        return {'width':f'{width}px'}

    return app

@app.callback(Output('dummy', 'data-focused_row'),
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


@app.callback(Output('dummy', 'data-focused_elt'),
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

@app.callback(Output('dummy', 'data-row'),
             [Input('add_row', 'n_clicks_timestamp'),
              Input('reset', 'n_clicks_timestamp')])
def f(ts_add, ts_rst):
    global ACTIVE_ROWS
    global FOCUSED_ROW
    ts_add = 0 if ts_add is None else ts_add
    ts_rst = 0 if ts_rst is None else ts_rst
    if ts_add > ts_rst:
        row = ACTIVE_ROWS[ACTIVE_ROWS == 0].index.min()
        ACTIVE_ROWS[row] = 1
        FOCUSED_ROW = 0
        return row
    else:
        ACTIVE_ROWS = pd.Series(0, ACTIVE_ROWS.index)
        ACTIVE_ROWS[0] = 1
        FOCUSED_ROW = 'row_0'
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
    global ELT_WIDTH
    s = pd.Series(args[:-1], index=[f'item_{i}_{j}' for i, j in itertools.product(range(N_ROWS), range(N_ELEMENTS))])
    s['data'] = ts_data
    s['add'] = ts_add
    s['rmv'] = ts_rmv
    s = s.astype(float)
    if not s.dropna().empty and s.dropna().idxmax() == 'data':
        data = pd.DataFrame(args[-1])
        component = data.loc[data.Property == 'Component'].Value.values[0].capitalize()
        if component in var.component_properties.keys():
            new_data = pd.DataFrame([{'Property':'Component', 'Value':component}] + 
                                    [{'Property':p, 'Value':''} for p in var.component_properties[component]])
            for prop in data.Property.values:
                if prop in new_data.Property.values:
                    new_data.at[new_data.loc[new_data.Property == prop].index[0], 'Value'] = data.loc[data.Property==prop].Value.values[0]
            # if 'className' in new_data.Property.values:
            #     classes = new_data.at[new_data.loc[new_data.Property == 'className'].index[0], 'Value']
            #     new_data.at[new_data.loc[new_data.Property == 'className'].index[0], 'Value'] = classes
            ELT_PROPS[FOCUSED_ELEMENT] = new_data
            return new_data.to_dict('rows')
    data = ELT_PROPS[FOCUSED_ELEMENT]
    data.at[data.loc[data.Property == 'id'].index[0], 'Value'] = FOCUSED_ELEMENT if data.at[data.loc[data.Property == 'id'].index[0], 'Value'] == '' else data.at[data.loc[data.Property == 'id'].index[0], 'Value']
    classes = data.at[data.loc[data.Property == 'className'].index[0], 'Value'].split(' ')
    classes = list(set(classes) - set(var.numbers.values()))
    classes.insert(0, var.numbers[int(ELT_WIDTH[FOCUSED_ELEMENT] / DX)])
    if 'columns' not in classes:
        classes.append('columns')
    data.at[data.loc[data.Property == 'className'].index[0], 'Value'] = ' '.join(classes)
    return ELT_PROPS[FOCUSED_ELEMENT].to_dict('rows')

for id_row in range(N_ROWS):
    app = add_row_click_callback(app, f'row_{id_row}')
    app = add_row_focus_callback(app, f'row_{id_row}')
    for id_elt in range(N_ELEMENTS):
        app = add_element_class_callback(app, f'item_{id_row}_{id_elt}')
        app = add_element_style_callback(app, f'item_{id_row}_{id_elt}')

if __name__ == '__main__':
    app.run_server(debug=True)

