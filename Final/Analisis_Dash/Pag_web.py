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
WITH RentabilidadMensual AS (
    SELECT 
        n.Nombre_negocio,
        r.rentab_dia
    FROM 
        Entidad e
    JOIN 
        Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
    JOIN 
        Negocio n ON e.cod_negocio = n.cod_negocio
    WHERE 
        e.Fecha BETWEEN '2024-03-01' AND '2024-03-31'
),
MedianaRentabilidad AS (
    SELECT 
        Nombre_negocio,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rentab_dia) AS mediana_rentab_dia
    FROM 
        RentabilidadMensual
    GROUP BY 
        Nombre_negocio
),
TopPeores AS (
    SELECT 
        Nombre_negocio,
        mediana_rentab_dia
    FROM 
        MedianaRentabilidad
    ORDER BY 
        mediana_rentab_dia ASC
    LIMIT 5
),
TopMejores AS (
    SELECT 
        Nombre_negocio,
        mediana_rentab_dia
    FROM 
        MedianaRentabilidad
    ORDER BY 
        mediana_rentab_dia DESC
    LIMIT 5
)

SELECT * FROM TopMejores;
    """
    cursor.execute(consulta1)
    rows_can = cursor.fetchall()
    cons_1 = pd.DataFrame(rows_can, columns=['nombre_negocio', 'mediana_rentab_dia'])

    consulta8="""WITH RentabilidadMensual AS (
    SELECT 
        n.Nombre_negocio,
        r.rentab_dia
    FROM 
        Entidad e
    JOIN 
        Rentabilidad r ON e.cod_transaccion = r.cod_transaccion
    JOIN 
        Negocio n ON e.cod_negocio = n.cod_negocio
    WHERE 
        e.Fecha BETWEEN '2024-03-01' AND '2024-03-31'
),
MedianaRentabilidad AS (
    SELECT 
        Nombre_negocio,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rentab_dia) AS mediana_rentab_dia
    FROM 
        RentabilidadMensual
    GROUP BY 
        Nombre_negocio
),
TopPeores AS (
    SELECT 
        Nombre_negocio,
        mediana_rentab_dia
    FROM 
        MedianaRentabilidad
    ORDER BY 
        mediana_rentab_dia ASC
    LIMIT 5
),
TopMejores AS (
    SELECT 
        Nombre_negocio,
        mediana_rentab_dia
    FROM 
        MedianaRentabilidad
    ORDER BY 
        mediana_rentab_dia DESC
    LIMIT 5
)

SELECT * FROM TopPeores;"""

    cursor.execute(consulta8)
    rows_can = cursor.fetchall()
    cons_8= pd.DataFrame(rows_can, columns=['nombre_negocio', 'mediana_rentab_dia'])

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

    # Consultas escenario 4
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

    # Definir el layout de la aplicación
    app.layout = html.Div(children=[
        # INTRODUCCION
        html.H1("Análisis financiero del fondo de inversiones financiero Colombia para Marzo 2024", className='h1'),
        html.H2("Integrantes: ", className='h2'),
        html.Div([
            html.P("- Daniel Jose Morales Ramirez"),
            html.P("- Kevin Sebastian Canchila Rodrigez"),
            html.P("- Laura Sofia Ortiz Merchan"),
            html.P("- Juan Jose Reina Reyes ")
        ], className='inner-section-container'),
        html.H3("Idea del proyecto: ", className='h3'),
        html.Div([
            html.P("Para este proyecto se usó una base de datos del fondo de inversión colombiano para el mes de marzo del presente año en donde se pueden hacer análisis."),
            html.P("Para este proyecto se plantearon 4 escenarios de análisis para los cuales se harán consultas y gráficas correspondientes.")
        ], className='inner-section-container'),
        
        # ESCENARIOS
        # PRIMER ESCENARIO
        html.H2("Primer escenario: ", className='h2'),
        html.P("Identificar los negocios con mejores y peores variaciones diaria de rentabilidad", className='p'),
        
        dcc.Graph(id='Top',
                      figure = px.bar(cons_1, x='nombre_negocio', y='mediana_rentab_dia',
                    title='Top 5 mejores negocios',
                    color= 'nombre_negocio',
                    color_discrete_sequence=['#228B22']).update_layout(
                    height=700,
                ),
            className='graph'
                      ),
        dcc.Graph(id='Top2',
                      figure = px.bar(cons_8, x='nombre_negocio', y='mediana_rentab_dia',
                    title='Top 5 peores negocios',
                    color='nombre_negocio',
                    color_discrete_sequence=['#FF0000']).update_layout(
                    height=700,
                ),
            className='graph'
                      ),
        
        html.H3("Análisis del escenario: ", className='h3'),
        html.Div([
            html.P("Laura: Se identificaron los negocios con las mejores y peores variaciones diarias de rentabilidad. El negocio con la peor variación fue el Compartimiento B - FCP Deuda Infraestructura II Sura - Credicorp Capital, mientras que el negocio con la mejor variación, superando significativamente a los demás con una mediana de 662.7351 por día, fue el FCP 4G Credicorp Capital - Sura AM Comp Liquidez I."),
            html.P("Daniel: Con estas gráficas, podemos observar los 5 mejores y los 5 peores negocios según la variación diaria de la rentabilidad. Esto nos permite realizar el análisis necesario al momento de invertir. En esta parte del análisis, es importante tener en cuenta el negocio FCP 4G Credicorp Capital - Sura AM Comp Liquidez I, ya que ha mantenido una buena variación."),
            html.P("Kevin: Estas gráficas permiten identificar los negocios que sobresalen y aquellos que enfrentan dificultades, proporcionando una herramienta para la toma de decisiones estratégicas. Las variaciones en la rentabilidad diaria son indicadores críticos de desempeño, y su análisis puede guiar inversiones futuras."),
            html.P("Juan Jose: ")
        ], className='inner-section-container'),
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
        html.H3("Análisis del escenario: ", className='h3'),
        html.Div([
            html.P("Laura: La diversificación es una técnica que asigna inversiones a diferentes y variados activos para minimizar el riesgo. Esto implica una mezcla de diversos vehículos de inversión, así como exposiciones a distintas industrias y geografías. En nuestro análisis, se observó que las entidades menos diversificadas son ADCAP COLOMBIA S.A., FIDUCIARIA SURA S.A., y FIDUCIARIA DE OCCIDENTE S.A., mientras que la entidad más diversificada es Valores Bancolombia S.A. Esto asegura que ninguna entidad represente una proporción desproporcionada del riesgo total."),
            html.P("Daniel: Las entidades que aparecen en la parte superior de la gráfica, como ADCAP COLOMBIA S.A. y FIDUCIARIA SURA S.A., presentan los porcentajes más bajos. Esto sugiere que estas entidades están diversificando sus inversiones de manera más amplia, lo que reduce el riesgo asociado a la concentración en una sola inversión."),
            html.P("Kevin: Se puede identificar como tiene diversificado el fondo cada entidad, para lo cual las entidad que tienen un negocio que representa un gran porcentaje de su capital, existe un riesgo más alto de las que tienen una buena diversificación."),
            html.P("Juan Jose: ")
        ], className='inner-section-container'),
        
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
        html.Div([
            html.P("Laura: Para evaluar la consistencia y volatilidad de los rendimientos de cada entidad, se calcularon el coeficiente de variación y el porcentaje de cambio de los valores de fondo de cierre durante el mes de marzo. La entidad con el menor coeficiente de variación, indicando mayor consistencia, fue la Compañía de Profesionales de Bolsa, mientras que la entidad con mayor coeficiente de variación fue BBVA Valores Colombia S.A. Comisión. En cuanto al porcentaje de cambio, BBVA Valores Colombia S.A. Comisión presentó el mejor rendimiento positivo. La Compañía de Profesionales de Bolsa no mostró cambios a lo largo del mes, y Fiduciaria La Previsora S.A. tuvo el peor rendimiento con un cambio negativo."),
            html.P("Daniel: La entidad con la mayor disminución es FIDUCIARIA LA PREVISORA S.A., ubicada en el extremo derecho de la gráfica, con un porcentaje de cambio cercano al -20%. Además, esta entidad se encuentra entre las que presentan un mayor coeficiente de variación."),
            html.P("Kevin: El coeficiente de variación nos ayuda a analizar la volatilidad y que tan consistente son los rendimientos de cada entidad lo cual nos ayuda a concluir cuales son mas seguros debido a su baja volatilidad, respecto al promedio de crecimiento de las fondos a final de mes para poder hacer un decisión inteligente a la hora de invertir en alguna entidad."),
            html.P("Juan Jose: ")
        ], className='inner-section-container'),

        
        # CUARTO ESCENARIO
        html.H2("Cuarto escenario: ", className='h2'),
        html.P("Hallar la distribución de los fondos entre los diferentes subtipos de inversiones al cierre de marzo ", className='p'),

        dcc.Graph(
            id='grafica_torta',
            figure=px.pie(cons_5, values='porcentaje_total', names='nombre_subtipo', title='Proporciones de los subtipos de negocio con respecto al fondo', color_discrete_sequence=['#7DB3FF', '#7FFF7F', '#FFD700', '#FFB6C1', '#E6E6FA']),
            className='graph'
        ),

        
        html.H3("Análisis del escenario: ", className='h3'),
        html.Div([
            html.P("Laura: Al analizar la distribución de fondos entre diferentes subtipos de inversiones al cierre de marzo, se encontró que el subtipo predominante es el Fondo de Inversión Colectiva (FIC) de tipo general, que representa el 59.5% del total. En contraste, el subtipo con menor participación es el FIC Inmobiliario, con un 3.36%. Esta distribución refleja una preferencia significativa por los fondos de tipo general."),
            html.P("Daniel: Los subtipos de negocios que ocupan la mayor proporción en los fondos de inversión colombianos son los FIC de tipo general. Esto nos proporciona una visión clara de dónde es recomendable invertir este año."),
            html.P("Kevin: La distribución muestra una clara preferencia por los FIC de tipo general y los Fondos de Capital Privado, los cuales juntos representan más del 80% del fondo total. Esto sugiere una estrategia de inversión equilibrada entre diversificación general y apuestas significativas en activos privados. La menor proporción en FIC de Mercado Monetario, Bursátiles e Inmobiliarias indica una exposición más controlada a estos segmentos."),
            html.P("Juan Jose: ")
        ], className='inner-section-container'),
        
        # FINAL DEL ARCHIVO
        html.H3("Conclusiones generales", className='h3'),
        html.P("POR DEFINIR(IMPORTANTE)", className='p inner-section-container')
    ], className='section-container')

    # Ejecutar la aplicación
    if __name__ == '__main__':
        app.run_server(debug=True)

except Exception as ex:
    print(ex)

finally:
    if connection is not None:
        connection.close()
        print("Conexión cerrada")
