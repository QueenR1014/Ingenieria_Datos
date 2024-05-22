# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 11:03:59 2023

@author: JavierCasas
"""

import dash 
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px


data ={
       'x': [5,6,7,8,9] ,
'y': [12,15,18,13,6]
}

df = pd.DataFrame(data)

app =dash.Dash()
app.layout = html.Div(style={'backgroundColor':  '#111111'},children = [
    html.Div([
        html.H1('Hola curso 1', style={
            'text-align' : 'center',
            'color' :'#FFFFFF'})
        ]),
    html.Div('Dash esta corriendo', style ={
            'color' :'#FFFFFF'
        
        }),
    dcc.Graph(
        id = 'sample-graph',
        figure = px.line(df, x='x', y='y', title='Nombre de la gráfica')
        
        )
    ])

if __name__ == '__main__' :
    app.run_server(port=8085)