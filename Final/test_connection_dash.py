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


#Análisis de Rendimiento Histórico (Análisis 1)
sql_query = "SELECT n.cod_negocio, n.Nombre_negocio, r.rentab_año, r.rentab_dia, r.rentab_mes, r.rentab_sem FROM rentabilidad r JOIN entidad e ON r.cod_transaccion = e.cod_transaccion JOIN negocio n ON e.cod_negocio = n.cod_negocio;" #query de testeo

df = pd.read_sql(sql_query,conn) #referencia el sql query a la conexión

#iterar sobre todas las columnas de Rentabilidad
rentab_columns = [col for col in df.columns if col.startswith('rentab_')]

app.layout = html.Div([
    html.H1('Análisis de Rendimiento Histórico', style = {
        'text-align':'center'
    }),
    *[dcc.Graph(
        id=f'rentabilidad-{col}',
        figure=px.bar(df[['cod_negocio', col]].iloc[0:9], 
                      x='cod_negocio', y=col, title=f'Relación Negocio-{col}').update_layout(
                          xaxis_title='Código del Negocio',
                          yaxis_title=col
                      )
    ) for col in rentab_columns]
])

conn.close()

if __name__ == '__main__':
    app.run_server(port=8085) 