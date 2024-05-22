import pandas as pd
import psycopg2 as psy2
import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


app = dash.Dash()

dbname = "Reporte_financiero_2024_03" #poner el nombre de la base de datos para hacer la conexión
user = "postgres" #poner el nombre del usuario destinado a la conexión de datos
password = "13031" #contraseña del usuario
host = "localhost" #servidor local

conn = psy2.connect(dbname = dbname, user = user, password=password, host = host)

sql_query = "Select * from Negocio;" #query de testeo

df = pd.read_sql(sql_query,conn) #referencia el sql query a la conexión

print(df[['cod_negocio','nombre_negocio']].iloc[0:9])
"""
if __name__ == '__main__':
    app.run_server(port=8085)"""