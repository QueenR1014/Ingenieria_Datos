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

    # Consultas escenario 1
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

    # Consultas escenario 2
    consulta2 = """
    WITH PorcentajePorNegocio AS (
        SELECT 
            e.Nombre_entidad,
            n.Nombre_negocio,
            SUM(r.valor_fondo_cierre) AS valor_fondo_cierre_negocio,
            (SUM(r.valor_fondo_cierre) / entidad_total.total_valor_fondo_cierre) * 100 AS porcentaje_total
        FROM 
            Entidad e
        JOIN 
            Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
        JOIN 
            Negocio n ON e.cod_negocio = n.cod_negocio
        JOIN 
            (SELECT 
                 e2.Nombre_entidad,
                 SUM(r2.valor_fondo_cierre) AS total_valor_fondo_cierre
             FROM 
                 Entidad e2
             JOIN 
                 Rentabilidad r2 ON e2.cod_transaccion = r2.cod_transaccion
             WHERE 
                 e2.Fecha = '2024-03-31'
             GROUP BY 
                 e2.Nombre_entidad) AS entidad_total
        ON 
            e.Nombre_entidad = entidad_total.Nombre_entidad
        WHERE 
            e.Fecha = '2024-03-31'
        GROUP BY 
            e.Nombre_entidad, n.Nombre_negocio, entidad_total.total_valor_fondo_cierre
    )
    SELECT 
        Nombre_entidad,
        MAX(porcentaje_total) AS porcentaje_max
    FROM 
        PorcentajePorNegocio
    GROUP BY 
        Nombre_entidad
    ORDER BY 
        porcentaje_max DESC;
    """
    cursor.execute(consulta2)
    rows_can = cursor.fetchall()
    cons_2 = pd.DataFrame(rows_can, columns=['nombre_entidad', 'porcentaje_max'])

    # Consultas escenario 3
    consulta3 = """
    WITH ValoresPorFecha AS (
        SELECT 
            e.Nombre_entidad,
            e.Fecha,
            SUM(r.valor_fondo_cierre) AS total_valor_fondo_cierre
        FROM 
            Entidad e
        JOIN 
            Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
        GROUP BY 
            e.Nombre_entidad, e.Fecha
    ),
    EstadisticasPorEntidad AS (
        SELECT 
            Nombre_entidad,
            AVG(total_valor_fondo_cierre) AS promedio_valor_fondo_cierre,
            STDDEV(total_valor_fondo_cierre) AS desviacion_estandar_valor_fondo_cierre
        FROM 
            ValoresPorFecha
        GROUP BY 
            Nombre_entidad
    )
    SELECT 
        Nombre_entidad,
        (desviacion_estandar_valor_fondo_cierre / promedio_valor_fondo_cierre) * 100 AS coeficiente_variacion
    FROM 
        EstadisticasPorEntidad
    ORDER BY 
        coeficiente_variacion DESC;
    """
    cursor.execute(consulta3)
    rows_can = cursor.fetchall()
    cons_3 = pd.DataFrame(rows_can, columns=['nombre_entidad', 'coeficiente_variacion'])

    # Consultas escenario 4
    consulta4 = """
    WITH ValoresPorFecha AS (
        SELECT 
            e.Nombre_entidad,
            e.Fecha,
            SUM(r.valor_fondo_cierre) AS total_valor_fondo_cierre
        FROM 
            Entidad e
        JOIN 
            Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
        WHERE 
            e.Fecha IN ('2024-03-01', '2024-03-31')
        GROUP BY 
            e.Nombre_entidad, e.Fecha
    ),
    ValoresInicio AS (
        SELECT 
            Nombre_entidad,
            total_valor_fondo_cierre AS valor_inicio
        FROM 
            ValoresPorFecha
        WHERE 
            Fecha = '2024-03-01'
    ),
    ValoresFin AS (
        SELECT 
            Nombre_entidad,
            total_valor_fondo_cierre AS valor_fin
        FROM 
            ValoresPorFecha
        WHERE 
            Fecha = '2024-03-31'
    )
    SELECT 
        vi.Nombre_entidad,
        ((vf.valor_fin - vi.valor_inicio) / vi.valor_inicio) * 100 AS porcentaje_cambio
    FROM 
        ValoresInicio vi
    JOIN 
        ValoresFin vf ON vi.Nombre_entidad = vf.Nombre_entidad
    ORDER BY 
        porcentaje_cambio DESC;
    """
    cursor.execute(consulta4)
    rows_can = cursor.fetchall()
    cons_4 = pd.DataFrame(rows_can, columns=['nombre_entidad', 'porcentaje_cambio'])

    consulta5 = """
    SELECT 
        s.Nombre_subtipo,
        (SUM(r.valor_fondo_cierre) / total.total_valor_fondo_cierre) * 100 AS porcentaje_total
    FROM 
        Entidad e
    JOIN 
        Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
    JOIN 
        Negocio n ON e.cod_negocio = n.cod_negocio
    JOIN 
        Subtipo s ON n.sub_negocio = s.id_ST
    JOIN 
        (SELECT 
             SUM(r2.valor_fondo_cierre) AS total_valor_fondo_cierre
         FROM 
             Entidad e2
         JOIN 
             Rentabilidad r2 ON e2.cod_transaccion = r2.cod_transaccion
         WHERE 
             e2.Fecha = '2024-03-31') AS total
    ON 
        e.Fecha = '2024-03-31'
    GROUP BY 
        s.Nombre_subtipo, total.total_valor_fondo_cierre
    ORDER BY 
        porcentaje_total DESC;
    """
    cursor.execute(consulta5)
    rows_can = cursor.fetchall()
    cons_5 = pd.DataFrame(rows_can, columns=['nombre_subtipo', 'porcentaje_total'])

    # Cerrar el cursor
    cursor.close()

    colores = {
        f'Entidad {chr(65 + i)}': px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
        for i in range(30)
    }

    # Crear la aplicación Dash
    app = Dash(__name__)

    # Crear un pivot table para el mapa de calor
    heatmap_data = rent_sem.pivot(index='nombre_entidad', columns='semana', values='rentab_sem_total')

    # Definir el layout de la aplicación
    app.layout = html.Div(children=[
        # INTRODUCCION
        html.H1("Análisis financiero del fondo de inversiones financiero Colombia para Marzo 2024", className='h1'),
        html.H2("Integrantes: ", className='h2'),
        html.Div([
            html.P("- Daniel Jose Morales Ramirez"),
            html.P("- Kevin Sebastian Canchila Rodrigez"),
            html.P("- Laura Sofia Ortiz Merchan"),
            html.P("- Juan Jose Reina Reyes (rol: jugar val)(DEBERIA ESTAR BRAYAN CANCHILA)")
        ], className='inner-section-container'),
        html.H3("Idea del proyecto: ", className='h3'),
        html.Div([
            html.P("Para este proyecto se usó una base de datos del fondo de inversión colombiano para el mes de marzo del presente año en donde se pueden hacer análisis."),
            html.P("Para este proyecto se plantearon 4 escenarios de análisis para los cuales se harán consultas y gráficas correspondientes.")
        ], className='inner-section-container'),
        
        # ESCENARIOS
        # PRIMER ESCENARIO
        html.H2("Primer escenario: ", className='h2'),
        html.P("Examinar el rendimiento histórico de marzo para cada entidad y así asegurar decisiones basadas en datos probados.", className='p'),
        
        # Dropdown para seleccionar entidades (Gráfico de líneas apiladas)
        dcc.Dropdown(
            id='entity-selector',
            options=[{'label': entidad, 'value': entidad} for entidad in rent_sem['nombre_entidad'].unique()],
            value=rent_sem['nombre_entidad'].unique().tolist(),  # valor por defecto
            multi=True,
            className='dropdown'
        ),
        
        # Gráfica de líneas apiladas
        dcc.Graph(id='area-chart', className='graph'),
        
        # Dropdown para seleccionar entidades (Mapa de calor)
        dcc.Dropdown(
            id='heatmap-entity-selector',
            options=[{'label': entidad, 'value': entidad} for entidad in rent_sem['nombre_entidad'].unique()],
            value=rent_sem['nombre_entidad'].unique().tolist(),  # valor por defecto
            multi=True,
            className='dropdown'
        ),
        
        # Mapa de calor
        dcc.Graph(id='heatmap1', className='graph'),
        
        html.H3("Análisis del escenario: ", className='h3'),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p inner-section-container'),
        
        # SEGUNDO ESCENARIO
        html.H2("Segundo escenario: ", className='h2'),
        html.P("Visualizar la diversificación de riesgos de las inversiones de cada entidad para identificar si alguna representa una parte desproporcionada del portafolio total.", className='p'),
        
        dcc.Graph(
            id='barras_hori',
            figure=px.bar(cons_2, x='porcentaje_max', y='nombre_entidad', title='Tabla de diversificación de las entidades', orientation='h', color_discrete_sequence=["#D60021"]).update_layout(
                height=1000
            ),
            className='graph'
        ),
        
        # TERCER ESCENARIO
        html.H2("Tercer escenario: ", className='h2'),
        html.P("Calcular el coeficiente de variación y el porcentaje de cambio de los valores de fondo de cierre de cada entidad para evaluar la consistencia y volatilidad de sus rendimientos y medir el crecimiento o la disminución en el valor del fondo a lo largo del mes de marzo.", className='p'),
        
        dcc.Graph(
            id='GRAF_VIOLIN',
            figure=px.violin(cons_3, 
                x='nombre_entidad',   
                y='coeficiente_variacion',       
                color='nombre_entidad',  
                box=True,          
                points='all',      
                hover_data=['coeficiente_variacion'],  
                title='Distribución de los coeficientes de variación entre las entidades').update_layout(
                height=800
            ),
            className='graph'
        ), 

        dcc.Graph(
            id='grafica_barras_vambio',
            figure=px.bar(cons_4, x='nombre_entidad', y='porcentaje_cambio', title='Porcentaje de Cambio en el Valor del Fondo de Cierre por Entidad',  
                color=cons_4['porcentaje_cambio'] > 0,
                color_discrete_map={True: '#2CA02C', False: '#D62728'}
            ).update_layout(
                height=900,
                showlegend=False,
                updatemenus=[
                    dict(
                        buttons=[
                            dict(
                                args=[{'visible': [True, True]}],
                                label='Mostrar Ambos',
                                method='update'
                            ),
                            dict(
                                args=[{'visible': [True, False]}],
                                label='Mostrar Positivos',
                                method='update'
                            ),
                            dict(
                                args=[{'visible': [False, True]}],
                                label='Mostrar Negativos',
                                method='update'
                            )
                        ],
                        direction="down",
                        showactive=True,
                        x=1,
                        xanchor="left",
                        y=1,
                        yanchor="top"
                    )
                ]
            ),
            className='graph'
        ),

        html.H3("Análisis del escenario: ", className='h3'),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p inner-section-container'),

        
        # CUARTO ESCENARIO
        html.H2("Cuarto escenario: ", className='h2'),
        html.P("comprender cómo se distribuyen los fondos entre los diferentes subtipos de inversiones al cierre de marzo ", className='p'),

        dcc.Graph(
            id='grafica_torta',
            figure=px.pie(cons_5, values='porcentaje_total', names='nombre_subtipo', title='Proporciones de los subtipos de negocio con respecto al fondo', color_discrete_sequence=['#7DB3FF', '#7FFF7F', '#FFD700', '#FFB6C1', '#E6E6FA']),
            className='graph'
        ),

        
        html.H3("Análisis del escenario: ", className='h3'),
        html.P("CONCLUSIONES DEL CASO(PENDIENTE)", className='p inner-section-container'),
        
        # FINAL DEL ARCHIVO
        html.H3("Conclusiones generales", className='h3'),
        html.P("POR DEFINIR(IMPORTANTE)", className='p inner-section-container')
    ], className='section-container')

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
