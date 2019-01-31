import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.offline as py
from dash.dependencies import Input, Output, State

# import callbacks

FOCUSED = '.'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # dcc.Interval(id='update_focus', interval=1000, n_intervals=0),
    html.Div([
        # html.H4('App Maker'),
        html.Div([
            # html.Div([html.Div(className='draggable', id='item_1')], className='row', n_clicks=0, id='row_1'),
        ], id='div_maker', className='maker')
    ]),
    html.Button('Add row', id='add_row', n_clicks=0),
    html.Button('Add element', id='add_element', n_clicks=0),
    html.Div(id='dummy')
])

app.scripts.append_script({"external_url": "http://code.interactjs.io/v1.3.4/interact.min.js"})

def add_item_callback(app, id):
    print('ADDING CALLBACK FOR {}'.format(id))

    @app.callback(Output(id, 'data-dummy'),
                 [Input(id, 'n_clicks')])
    def f(n):
        if n is not None:
            print(n)
        global FOCUSED
        FOCUSED = id
        return n

    return app


@app.callback(Output('div_maker', 'children'),
             [Input('add_row', 'n_clicks')],
             [State('div_maker', 'children')])
def f(n, children):
    global app
    if n is None:
        n = 0
    row = html.Div(className='row', n_clicks=0, id='row_{}'.format(n))
    if children is None:
        out = [row]
    else:
        out = children + [row]
    app.layout.children[0].children[0].children.append(row)
    app = add_item_callback(app, 'row_{}'.format(n))
    print(app.callback_map)
    return out

@app.callback(Output('add_element', 'data-dummy'),
             [Input('add_element', 'n_clicks')])
def f(n):
    global app
    app.layout.children.append(html.Div('Hello world'))
    print(app.run_server(debug=True))
    # print(dir(app))
    if n > 0:
        print('FOCUSED:', FOCUSED)


# for item in ['div_maker']:#, 'item_1', 'row_1']:
#     app = add_item_callback(app, item)

if __name__ == '__main__':
    app.run_server(debug=True)

# {'div_maker.children': {'inputs': [{'id': 'add_row', 'property': 'n_clicks'}], 'state': [{'id': 'div_maker', 'property': 'children'}], 'events': [], 'callback': <function f at 0x000002B07D870EA0>},
#  'add_element.data-dummy': {'inputs': [{'id': 'add_element', 'property': 'n_clicks'}], 'state': [], 'events': [], 'callback': <function f at 0x000002B07D8AB048>},
#  'row_0.data-dummy': {'inputs': [{'id': 'row_0', 'property': 'n_clicks'}], 'state': [], 'events': [], 'callback': <function add_item_callback.<locals>.f at 0x000002B07D967268>}}