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

sql_query = "SELECT n.cod_negocio, n.Nombre_negocio, r.rentab_año FROM rentabilidad r JOIN entidad e ON r.cod_transaccion = e.cod_transaccion JOIN negocio n ON e.cod_negocio = n.cod_negocio;;" #query de testeo

df = pd.read_sql(sql_query,conn) #referencia el sql query a la conexión

#print(df[['cod_negocio','nombre_negocio']].iloc[0:9])

app.layout = html.Div([
    html.H1('Rentabilidad Anual Negocio', style = {
        'text-align':'center'
    }),
    dcc.Graph(
        id = 'rentabilidad-anual',
        figure = px.bar(df[['cod_negocio','rentab_año']].iloc[0:9], 
                x = 'cod_negocio', y = 'rentab_año', title = 'Relación Negocio-Rentabilidad').update_layout(
                    xaxis_title = 'Código del Negocio',
                    yaxis_title = 'Rentabilidad Anual'
                )
    )
])

conn.close()

if __name__ == '__main__':
    app.run_server(port=8085)