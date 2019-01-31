from dash.dependencies import Input, Output, State

FOCUSED = ''

def add_item_callback(app, id):

    @app.callback(Output(id, 'data-dummy'),
                 [Input(id, 'n_clicks')])
    def f(n):
        if n is not None and n > 0:
            FOCUSED = id
            print(id)

    return app