import dash_core_components as dcc
import dash_html_components as html

elements = sorted(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'dropdown', 'button', 'graph', 'tabs'])

component_properties = {item.lower(): eval(f'dcc.{item}(id="dummy").available_properties') for item in dir(dcc) if '_' not in item and item != 'version'}
component_properties.update({item.lower(): eval(f'html.{item}(id="dummy").available_properties') for item in dir(html) if '_' not in item and item != 'version'})
