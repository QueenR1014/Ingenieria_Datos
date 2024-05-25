import pandas as pd
from dash import Dash, html, dcc, Input, Output
import psycopg2
import plotly.express as px

# Establecer conexión con la base de datos PostgreSQL
try:
    connection = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='13031',
        database='Reporte_financiero_2024_03',
        port='5432',
    )
    print("Conexión exitosa")

    # Crear un cursor para ejecutar comandos SQL
    cursor = connection.cursor()

    # Ejecutar la consulta SQL para obtener la rent_sem_tot por negocio de cada entidad
    consulta1 = """
    SELECT i.Nombre_entidad, AVG(r.rentab_dia) AS rentab_sem_total,
    CASE
        WHEN EXTRACT(DAY FROM e.Fecha) BETWEEN 1 AND 7 THEN 'Semana 1'
        WHEN EXTRACT(DAY FROM e.Fecha) BETWEEN 8 AND 14 THEN 'Semana 2'
        WHEN EXTRACT(DAY FROM e.Fecha) BETWEEN 15 AND 21 THEN 'Semana 3'
        WHEN EXTRACT(DAY FROM e.Fecha) BETWEEN 22 AND 31 THEN 'Semana 4'
    END AS Semana
    FROM Entidad e
    JOIN Identificacion i ON e.Nombre_entidad = i.Nombre_entidad
    JOIN Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
    WHERE DATE_PART('month', e.Fecha) = 3 AND DATE_PART('year', e.Fecha) = 2024
    GROUP BY i.Nombre_entidad, Semana
    ORDER BY Semana;
    """
    cursor.execute(consulta1)
    rows_can = cursor.fetchall()
    rent_sem = pd.DataFrame(rows_can, columns=['nombre_entidad', 'rentab_sem_total', 'semana'])

    # Cerrar el cursor
    cursor.close()

    # Crear la aplicación Dash
    app = Dash(__name__)

    # Crear un pivot table para el mapa de calor
    heatmap_data = rent_sem.pivot(index='nombre_entidad', columns='semana', values='rentab_sem_total')

    # Definir el layout de la aplicación
    app.layout = html.Div(children=[
        # INTRODUCCION
        html.H1("Análisis financiero del fondo de inversiones financiero Colombia para Marzo 2024"),
        html.H2("Integrantes: "),
        html.P("- Daniel Jose Morales Ramirez", className='p'),
        html.P("- Kevin Sebastian Canchila Rodrigez", className='p'),
        html.P("- Laura Sofia Ortiz Merchan", className='p'),
        html.P("- Juan Jose Reina Reyes (rol: jugar val y hacer pdf's)", className='p'),
        html.H3("Idea del proyecto: "),
        html.P("Para este proyecto se usó una base de datos del fondo de inversión colombiano para el mes de marzo del presente año en donde se pueden hacer análisis.", className='p'),
        html.P("Para este proyecto se plantearon 4 escenarios de análisis para los cuales se harán consultas y gráficas correspondientes.", className='p'),
        
        # ESCENARIOS
        # PRIMER ESCENARIO
        html.H2("Primer escenario: "),
        html.P("Examinar el rendimiento histórico de marzo para cada entidad y así asegurar decisiones basadas en datos probados.", className='p'),
        
        # Dropdown para seleccionar entidades (Gráfico de líneas apiladas)
        dcc.Dropdown(
            id='entity-selector',
            options=[{'label': entidad, 'value': entidad} for entidad in rent_sem['nombre_entidad'].unique()],
            value=rent_sem['nombre_entidad'].unique().tolist(),  # valor por defecto
            multi=True
        ),
        
        # Gráfica de líneas apiladas
        dcc.Graph(id='area-chart'),
        
        # Dropdown para seleccionar entidades (Mapa de calor)
        dcc.Dropdown(
            id='heatmap-entity-selector',
            options=[{'label': entidad, 'value': entidad} for entidad in rent_sem['nombre_entidad'].unique()],
            value=rent_sem['nombre_entidad'].unique().tolist(),  # valor por defecto
            multi=True
        ),
        
        # Mapa de calor
        dcc.Graph(id='heatmap1'),
        
        html.H3("Análisis del escenario: "),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p'),
        
        # SEGUNDO ESCENARIO
        html.H2("Segundo escenario: "),
        html.P("Mantener la diversificación en las inversiones del fondo, asegurando que ninguna entidad o tipo negocio representa una parte desproporcionada del portafolio total.", className='p'),
        dcc.Graph(id='esc_2'),  # *cantidad de gráficos
        html.H3("Análisis del escenario: "),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p'),
        
        # TERCER ESCENARIO
        html.H2("Tercer escenario: "),
        html.P("Definir criterios claros y objetivos para la selección de negocios y entidades, incluyendo rentabilidad esperada, estabilidad financiera, y potencial de crecimiento.", className='p'),
        dcc.Graph(id='esc_3'),  # *cantidad de gráficos
        html.H3("Análisis del escenario: "),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p'),
        
        # CUARTO ESCENARIO
        html.H2("Cuarto escenario: "),
        html.P("Por definir", className='p'),
        dcc.Graph(id='esc_4'),  # *cantidad de gráficos
        html.H3("Análisis del escenario: "),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p'),
        
        # FINAL DEL ARCHIVO
        html.H3("Conclusiones generales"),
        html.P("POR DEFINIR(IMPORTANTE)", className='p')
    ])

    # Definir el callback para actualizar la gráfica de área en función de la selección de entidades
    @app.callback(
        Output('area-chart', 'figure'),
        Input('entity-selector', 'value')
    )
    def update_area_chart(selected_entities):
        filtered_data = rent_sem[rent_sem['nombre_entidad'].isin(selected_entities)]
        fig = px.line(filtered_data, x='semana', y='rentab_sem_total', color='nombre_entidad',
                      title='Tendencia de Rentabilidad Promedio Diaria por Entidad y Semana en Marzo 2024',
                      labels={'rentab_sem_total': 'Rentabilidad Promedio Diaria', 'semana': 'Semana', 'nombre_entidad': 'Entidad'})
        return fig

    # Definir el callback para actualizar el mapa de calor en función de la selección de entidades
    @app.callback(
        Output('heatmap1', 'figure'),
        Input('heatmap-entity-selector', 'value')
    )
    def update_heatmap(selected_entities):
        filtered_data = heatmap_data.loc[selected_entities]
        fig = px.imshow(
            filtered_data,
            labels=dict(x="Semana", y="Entidad", color="Rentabilidad"),
            title='Mapa de Calor de Rentabilidad por Entidad y Semana'
        ).update_layout(
            height=800
        )
        return fig

    # Ejecutar la aplicación
    if __name__ == '__main__':
        app.run_server(debug=True)

except Exception as ex:
    print(ex)

finally:
    if connection is not None:
        connection.close()
        print("Conexión cerrada")
