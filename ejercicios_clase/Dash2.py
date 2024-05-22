# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 12:16:11 2023

@author: JavierCasas
"""

import pandas as pd
import psycopg2 as psy2
import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px



dbname = "Book_exercise1"
user = "javier"
password = "123456"
host = "localhost"


conn = psy2.connect(dbname =dbname, user = user, password = password, host = host)

sql_query = "Select * from student;"

df =pd.read_sql(sql_query, conn)

#print (df.iloc[0:9])

print (df[['id','tot_cred']].iloc[0:9])

app =dash.Dash()
app.layout = html.Div([
    html.H1('Hola curso 1', style={'text-align' : 'center'}),
    html.Div('Dash esta corriendo'),
    dcc.Graph(
        id = 'sample-graph',
        figure = px.bar(df[['id','tot_cred']].iloc[0:9], x='id', y='tot_cred', title='Nombre de la gráfica').update_layout(
            xaxis_title = 'Id Student',
            yaxis_title = 'Total Créditos'
            )
        
        )
    ])


conn.close()

if __name__ == '__main__' :
    app.run_server(port=8085)