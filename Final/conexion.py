import psycopg2 # Importamos la librería psycopg2 

try:
    # Intentamos establecer una conexión con la base de datos PostgreSQL
    connection = psycopg2.connect(
        host='localhost',  # Dirección del servidor de base de datos
        user='postgres',  # Nombre de usuario
        password='123456789',  # Contraseña del usuario
        database='Reporte_financiero_2024_03',  # Nombre de la base de datos a la que queremos conectarnos
        port='5433', # Puerto en el que está escuchando el servidor de base de datos
    )
    print("Conexión exitosa") # Si la conexión es exitosa, imprimimos un mensaje
    cursor = connection.cursor() # Creamos un objeto cursor para ejecutar comandos SQL


    # Tabla1 Entidad
    cursor.execute("SELECT * FROM Entidad   ")  
    rows_tabla_Entidad = cursor.fetchall()  
    for row in rows_tabla_Entidad:
        print(row)

    # Tabla2 Negocio	
    cursor.execute("SELECT * FROM Negocio") 
    rows_Negocio = cursor.fetchall()  
    for row in rows_Negocio:
        print(row)

    # Tabla3 Identificacion
    cursor.execute("SELECT * FROM Identificacion") 
    rows_Identificacion = cursor.fetchall() 
    for row in rows_Identificacion:
        print(row)

    # Tabla4 Subtipo
    cursor.execute("SELECT * FROM Subtipo")  
    rows_Subtipo = cursor.fetchall()  
    for row in rows_Subtipo:
        print(row)

    # Tabla5 Jerarquia
    cursor.execute("SELECT * FROM Jerarquia")  
    rows_Jerarquia = cursor.fetchall()  
    for row in rows_Jerarquia:
        print(row)

    # Tabla6 Rentabilidad
    cursor.execute("SELECT * FROM Rentabilidad")  
    rows_Rentabilidad = cursor.fetchall()  
    for row in rows_Rentabilidad:
        print(row)


except Exception as ex:
    print(ex) # Si ocurre algún error durante la ejecución del bloque try, lo capturamos y lo imprimimos
    
finally:
    connection.close() # Finalmente, independientemente de si hubo éxito o error, cerramos la conexión a la base de datos
    print("Conexión finalizada") # Imprimimos un mensaje para indicar que la conexión ha sido cerrada