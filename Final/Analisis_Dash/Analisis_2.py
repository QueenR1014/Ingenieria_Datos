import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)

# Create a SQLAlchemy engine
engine = create_engine('postgresql://username:password@localhost:5432/database_name')

# Query to fetch necessary data
sql_query = """
SELECT 
    n.cod_negocio, 
    n.Nombre_negocio, 
    r.rentab_año, 
    r.rentab_dia, 
    r.rentab_mes, 
    r.rentab_sem 
FROM 
    rentabilidad r 
JOIN 
    entidad e ON r.cod_transaccion = e.cod_transaccion 
JOIN 
    negocio n ON e.cod_negocio = n.cod_negocio;
"""

df = pd.read_sql(sql_query, engine)
engine.dispose()  # Close the engine when done

# Extracting criteria-based columns
criteria_columns = ['rentab_año', 'rentab_dia', 'rentab_mes', 'rentab_sem']

app.layout = html.Div([
    html.H1('Análisis de Rendimiento Histórico', style={'text-align': 'center'}),
    html.Div([
        html.Label('Rentabilidad Esperada (Anual):'),
        dcc.RangeSlider(
            id='rentab_año_slider',
            min=df['rentab_año'].min(),
            max=df['rentab_año'].max(),
            step=0.1,
            marks={i: f'{i}' for i in range(int(df['rentab_año'].min()), int(df['rentab_año'].max()) + 1)},
            value=[df['rentab_año'].min(), df['rentab_año'].max()]
        ),
    ]),
    html.Div([
        html.Label('Rentabilidad Diaria:'),
        dcc.RangeSlider(
            id='rentab_dia_slider',
            min=df['rentab_dia'].min(),
            max=df['rentab_dia'].max(),
            step=0.01,
            marks={i: f'{i}' for i in range(int(df['rentab_dia'].min()), int(df['rentab_dia'].max()) + 1)},
            value=[df['rentab_dia'].min(), df['rentab_dia'].max()]
        ),
    ]),
    html.Div([
        html.Label('Rentabilidad Mensual:'),
        dcc.RangeSlider(
            id='rentab_mes_slider',
            min=df['rentab_mes'].min(),
            max=df['rentab_mes'].max(),
            step=0.1,
            marks={i: f'{i}' for i in range(int(df['rentab_mes'].min()), int(df['rentab_mes'].max()) + 1)},
            value=[df['rentab_mes'].min(), df['rentab_mes'].max()]
        ),
    ]),
    html.Div([
        html.Label('Rentabilidad Semanal:'),
        dcc.RangeSlider(
            id='rentab_sem_slider',
            min=df['rentab_sem'].min(),
            max=df['rentab_sem'].max(),
            step=0.1,
            marks={i: f'{i}' for i in range(int(df['rentab_sem'].min()), int(df['rentab_sem'].max()) + 1)},
            value=[df['rentab_sem'].min(), df['rentab_sem'].max()]
        ),
    ]),
    html.Div(id='output-container-range-slider'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        page_size=10
    )
])

@app.callback(
    Output('table', 'data'),
    Input('rentab_año_slider', 'value'),
    Input('rentab_dia_slider', 'value'),
    Input('rentab_mes_slider', 'value'),
    Input('rentab_sem_slider', 'value')
)
def update_table(rentab_año_range, rentab_dia_range, rentab_mes_range, rentab_sem_range):
    filtered_df = df[
        (df['rentab_año'] >= rentab_año_range[0]) & (df['rentab_año'] <= rentab_año_range[1]) &
        (df['rentab_dia'] >= rentab_dia_range[0]) & (df['rentab_dia'] <= rentab_dia_range[1]) &
        (df['rentab_mes'] >= rentab_mes_range[0]) & (df['rentab_mes'] <= rentab_mes_range[1]) &
        (df['rentab_sem'] >= rentab_sem_range[0]) & (df['rentab_sem'] <= rentab_sem_range[1])
    ]
    return filtered_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
