#V1     ->  crea un excel con datos basicos (Nombre, Latitud, Longitud, Tipo de Edificio) de los edificios de un territorio dado
#V2     ->  coordenadas relativas a las estradas de los edificios
#V3     ->  df solo de viviendas y mete el nombre del territorio
#V4     ->  df viviendas tiene los datos de viviendas de todos los distritos
#V5     ->  se introduccen los refugios interiores y una funcion para determinar a hora y fecha dada si estan abiertos
#V6     ->  "obtener_edificios_mas_cercanos" genera una lista de "n" refugios climaticos más cercanos al edificio
#V7     ->  Se genera un excel con el refugio disponible más cercano a cada hora
#V8     ->  Se incluyen los refugios exteriores
#V9     ->  Nuevo Excel con la media de distancia minima por territorio y fecha
#V10    ->  Mejoras en la Experiencia de Usuario
# --------------------------------------------------------------------------------------------------------------------------
#Nota   ->  Tras un parón potente, se retoma el codigo.
#           Basicamente, se aprecian problemas de optimización que provocan tiempos de computación no-aceptables.
#           De momento estoy haciendo cambios menores en el codigo para poder horientarme mejor
# --------------------------------------------------------------------------------------------------------------------------
#V11    ->  Se optimiza bastante la inicializacion del sistema, guardando los datos en una carpeta, en vez de cargarlos cada vez
#       ->  Es necesario optimizar los tiempos de computo por edificio, así como separar la busqueda de exteriores e interiores
#           para estudiar las diferencias con respecto a climatizacion (especialmente para invierno, pues los exteriores sirven
#           más para verano).
#V12    ->  Se provee más informacion en el csv de salida ['Data','Territory','Coords','','','','','','','']
#           y se optimiza la busqueda de edificios cercanos. 
#           [Error] Los refugios no detectan el distrito al que pertenecen
#                   Los refugios externos deberian ir como geometria (quizas todos los refugios?). 
#                   Algunos refugios no detectan coordenadas.
#                   Desnivel (hay tenams de esos en la libreria OSMx)
#V13    ->  Cambios menores
#V14    ->  Cambios menores
#V15    ->  Se modifican los datos de entrada
#           ->V15.2.4 Mejora el sistema de creado de df de refugios. SOLO crea un csv llamado experiment en DATA con los datos de 
#             los refugios interiores.
#           ->V15.3 Crea todos los elementos necesarios pero no actua con las geometrias
#           ->V15.4 Se ha corregido el tema de las distancias
#V16    ->  Modificacion en el calculo de rutas para agilizar el proceso
#           ->V16.1 Se ha logrado que calcule bien las rutas y rapido
#           ->V16.2 Actua pero lento
#           ->V16.4 Se ha modificado para que actue más rapido, pero aun deja que desear
#             MEJORA: aprox. la mitad del tiempo original
#V17    ->  Se realizan algunas modificaciones para acelerar los calculos
#            ->V17.1 Se guardan los calculos reaalizados para cada escenario de apertura de edificios haciendo que solo se calculen una vez por situacion
#              MEJORA: computar 8784 escenarios por building -> computar 295 escenarios por building (reduccion del 96.64% del esfuerzo original)
#V18    ->  Se añade el calculo de metros subidos y bajados
#V19    ->  Se SUPRIMEN los REFUGIOS DE EXTERIOR y se sustitulle por POSIBLES REFUGIOS
#V20    ->  Se realizan mejoras para la eficiencia del codigo
#           ->V20.1 Basicamente, se crean archivos en Datapath por cada building ordenaditos por cercania
#           ->V20.2 Se limpia el codigo anterior
#           ->V20.3 El codigo busca y lee los documentos para evaluar si ya han sido creados
#           [ERROR] Se ha detectado un error en la generacion de los refugios posibles, ya se ha corregido (line 100)
#V21    ->  Se añade el tratamiento de los datos tras su computacion
#           ->V21.1 Se reincorpora el guardar tipos de escenarios para reducir la carga computacional
#           ->V21.2 Correcciones menores
#           ->V21.3 Crea un df con el fitness por hora
#           [ERROR] Se ha detectado algún tipo de error al evaluar los edificios abiertos cada hora. Ej. El Archivo Historico sale a algunas horas abierto
#           y a otras cerrado, cuando se supone que abre a las 9:00. 
#           ->V21.4 Error corregido, pero se ha inhabilitado la funcion de la V21.1
#           ->V21.5 errores menores
#           ->V21.6 rererehabilitado la funcion de la V21.1 y errores menores corregidos
#V22    ->  Guardar un df que especifique por hora cuantos refugios estan abiertos (dia, hora, numero) para graficas y comparativas
#V23    ->  Mejora considerable de la eficiencia en casos de horarios repetidos (mismos edificios abiertos)
#V24    ->  Implementacion del algoritmo de optimizacion de horarios
#           ->V24.2 Separacion de la funcion del main y correcciones y creacion de elementos por dias, semanas, meses, estaciones y año
#           ->V24.3 Se añade la columna 'building_type_name' a los resultados de la optimizacion
#             y se corrige un error, que point_list no se filtraba y luego se trabajaba tambien con edificios que existian :S
#V25    ->  [ERROR] Se detecta un bug al cargar la computacion previa de optimizacion, siempre salta al punto del 37% (¿?)
#V26    ->  Mejoras de rendimiento.
#           -> Se crea refugios_v3 adaptando mejor el tema de los horarios de invierno y verano (hipotesis; h.verano = julio + agosto)           
#V27    ->  Se modifica lo que se considera refugio, ampliandolo a casetas de monte, estaciones de tren y estadios

#Cosas por hacer:   ->Refugios, meter tambien fechas festivas, que sabemos que días fueron en 2024
#
#Opcionales         ->Modificar el analisis, en vez de por edificios crear una red homogenea por el territorio con un distanciamineto entre puntos
#                     determinado.
#                   ->Se detectan errorers en la asignacion de algunos edificios con sus distritos. He comprobado alguno y deberiaen estar bien.


import os
import ast
import srtm
import numpy as np
import osmnx as ox
import pandas as pd
from tqdm import tqdm
import networkx as nx
import geopandas as gpd
from pathlib import Path
from datetime import datetime, timedelta
from refugios_v3 import horarios, meses_espanol_a_ingles, ref_ext, dict_osmid_refug

building = {"building": ["apartments", "barracks", "bungalow", "cabin", "detached", "annexe", "dormitory",
    "farm", "house", "houseboat", "residential", "semidetached_house", "static_caravan",
    "stilt_house", "terrace", "trullo", "yes"]}

poss_ref = {"building": ["public","train_station"],
            "amenity": [
                "public", "townhall", "sport_centre", "information", 
                "mall", "library", "museum", "community_centre", "arts_centre", 
                "place_of_worship", "exhibition_centre", "school", "courthouse",
                "theatre", "police"],
            "leisure": ["sport_centre", "stadium"],
            "tourism": ["museum", "hostel", "alpine_hut"],
            "shop": "mall",
            "railway":	"subway_entrance"}

def get_osm_elements(area_name, poss_ref):
    """
    Obtiene y filtra los elementos de OSM según un conjunto fijo de etiquetas y prioridades,
    y devuelve un DataFrame con la estructura personalizada.

    Parámetros:
    - area_name (str): Nombre del área para buscar datos.
    - poss_ref (dict): Reglas de prioridad para las etiquetas.

    Retorna:
    - DataFrame: Datos filtrados con las claves `name`, `osm_id`, `geometry`, `lat`, `lon`.
    """
    # Conjunto fijo de etiquetas a consultar
    tags = {
        "building": True,
        "amenity": True,
        "leisure": True,
        "tourism": True,
        "shop": True,
        "railway": True
    }
    
    # Descargar datos de la zona especificada
    gdf = ox.features_from_place(area_name, tags)
    
    # Convertir a DataFrame
    data = gdf.reset_index()

    # Crear la estructura personalizada
    filtered_data = []
    b_num = 0  # Contador para los nombres

    for _, row in data.iterrows():
        for key, values in poss_ref.items():
            if key in row and pd.notna(row[key]):
                if isinstance(values, list):  # Si hay una lista de valores aceptados
                    if row[key] in values:
                        break
                elif row[key] == values:  # Si el valor aceptado es único
                    break
        else:
            # Si ninguna clave cumple, continuar con la siguiente fila
            continue
        building_type_name = building_type(row, poss_ref)
        osmid_reformed = osmid_reform(row)
        
        if osmid_reformed in dict_osmid_refug:
            continue
        
        # Añadir los datos con la estructura personalizada
        filtered_data.append({
            'name': f'building_{b_num}',
            'building_type_name':building_type_name,
            'osm_id': osmid_reformed,
            'geometry': row['geometry'],
            'lat': row['geometry'].centroid.y if row['geometry'] is not None else None,
            'lon': row['geometry'].centroid.x if row['geometry'] is not None else None,
        })
        b_num += 1  # Incrementar el contador

    # Convertir a DataFrame final
    return pd.DataFrame(filtered_data)

def osmid_reform(row):
    osmid = row.get('osmid')
    element_type = row.get('element_type')

    if pd.isna(osmid) or pd.isna(element_type):
        return None  # Si faltan datos, devolver None
    
    # Determinar el prefijo basado en el tipo del elemento
    if element_type.lower() == 'node':
        return f'N{osmid}'
    elif element_type.lower() == 'relation':
        return f'R{osmid}'
    elif element_type.lower() == 'way':
        return f'W{osmid}'

    # Si no es un tipo válido, devolver None
    return None

def building_type(row, poss_ref):
    # Revisar cada categoría en orden de prioridad
    for category, values in poss_ref.items():
        actor = row[category] if category in row and pd.notna(row[category]) else False
        
        # Verificar si el valor de la categoría está en las prioridades definidas
        if actor:
            if isinstance(values, list):  # Si las prioridades son una lista
                if actor in values:
                    return f'{category}_{actor}'
            elif actor == values:  # Si la prioridad es un valor único
                return f'{category}_{actor}'

    # Si no se encuentra ninguna coincidencia
    return 'unknown'

def obtener_geometrias(osmid_list, type=0):
    data = []  # Cambiamos a lista para almacenar cada resultado como un diccionario
    if type == 1:
        data = get_osm_elements(osmid_list[0], osmid_list[1])
        return data
    for o, osmid in enumerate(osmid_list):
        if type == 1:
            name = f'building_{o}'
        try:
            # Usamos OSMnx para obtener el polígono de la ubicación
            for clave, valor in dict_osmid_refug.items():
                if valor == osmid:
                    name = clave
                    break  # Salir del bucle después de encontrar la primera coincidencia
            try:
                area = ox.geocode_to_gdf(osmid, by_osmid=True)
            except Exception:
                continue
            # Guardamos la geometría en el diccionario si no está vacío
            if not area.empty:
                # Algunas geometrías no tienen 'lat' y 'lon', por lo que verificamos su existencia
                data.append({
                    'name': name,
                    'osm_id': osmid,
                    'geometry': area.iloc[0]["geometry"],
                    'lat': area.iloc[0]["geometry"].centroid.y if area.iloc[0]["geometry"] is not None else None,
                    'lon': area.iloc[0]["geometry"].centroid.x if area.iloc[0]["geometry"] is not None else None,
                })
            else:
                print(f'Ubicación "{dict_osmid_refug[osmid]}" no tiene datos (o no se ha detectado).')
        except Exception as e:
            # Si ocurre un error, lo registramos
            print(f"Error al obtener geometría para {dict_osmid_refug[osmid]}: {e}")
    return data

def obtener_dataframe_direcciones(data, districts, type): 
    """Obtiene un DataFrame con las coordenadas de cada dirección y asigna un 'Territorio' (distrito)."""
    print('Procesando datos...')
    districts_osmid = []
    for district in districts:
        districts_osmid.append(dict_osmid_refug[district])
    districts_data = obtener_geometrias(districts_osmid)
    
    # Crear un GeoDataFrame con los distritos y sus geometrías
    gdf_distrits = gpd.GeoDataFrame(districts_data, columns=["name", "geometry"])
    gdf_distrits.set_crs("EPSG:4326", allow_override=True, inplace=True)
        
    # Crear DataFrame de refugios y convertirlo en un GeoDataFrame
    data_osmid = []
    if type == 1:
        data_osmid = data
    else:
        for d in data:
            data_osmid.append(dict_osmid_refug[d])
    refug_data = obtener_geometrias(data_osmid, type)
    df_refug_data = pd.DataFrame(refug_data)
    gdf_refug_data = gpd.GeoDataFrame(df_refug_data, geometry='geometry')
    gdf_refug_data.set_crs("EPSG:4326", inplace=True)

    # Realizar el join espacial para asignar el distrito correspondiente a cada refugio
    gdf_result = gpd.sjoin(gdf_refug_data, gdf_distrits[['name', 'geometry']], how='left', predicate='within')
    gdf_result = gdf_result.rename(columns={'name_right': 'subarea', 'name_left': 'name'})  # Renombramos la columna del distrito
    
    return gdf_result

def obtener_edificios_mas_cercanos(df1, df2, G, output_path):
    """
    Obtiene una lista con los nombres de los edificios más cercanos y la distancia caminada
    desde cada edificio en df1 a los edificios en df2.
    """
    if df2.empty:
        print("El DataFrame df2 está vacío. No se realizará ningún cálculo.")
        return
    
    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        print("El grafo G está vacío. No se puede calcular rutas.")
        return
    
    data = []

    # Extraer las coordenadas del edificio en df1
    lat1, lon1 = df1.lat, df1.lon
    
    try:
        # Encontrar el nodo más cercano al edificio en df1
        nodo_df1 = ox.distance.nearest_nodes(G, lon1, lat1)
    except Exception as e:
        print(df1)
        print(f"Error al encontrar el nodo más cercano para df1 ({lat1}, {lon1}): {e}")
        return

    # Iterar sobre cada fila en df2 para encontrar el edificio más cercano
    for row in df2.itertuples(index=False):
        lat2, lon2 = row.lat, row.lon
        
        # Calcular distancia euclidiana
        euc_dist = ox.distance.great_circle(lat1, lon1, lat2, lon2)
        if euc_dist > 500:  # Filtrar por distancia máxima
            continue

        try:
            # Encuentra el nodo más cercano en G
            nodo_df2 = ox.distance.nearest_nodes(G, lon2, lat2)

            # Encuentra la ruta más corta entre nodo_df1 y nodo_df2
            route = ox.shortest_path(G, nodo_df1, nodo_df2, weight='length')
            distance = nx.path_weight(G, route, weight="length")

            # Inicializar rise y fall
            rise, fall = 0, 0

            # Calcular desniveles a lo largo de la ruta
            for n, node in enumerate(route):
                actual_elevation = G.nodes[node].get('elevation', 0)
                if n > 0:  # Comparar con el nodo anterior
                    last_elevation = G.nodes[route[n - 1]].get('elevation', 0)
                    rise += max(actual_elevation - last_elevation, 0)
                    fall += max(last_elevation - actual_elevation, 0)

            # Obtener tipo de edificio
            building_type = getattr(row, 'building_type_name', "N/A")

            # Agregar los datos al listado
            data.append({
                'territory': getattr(row, 'subarea', "Unknown"),
                'building_type': building_type,
                'osmid': getattr(row, 'osm_id', None),
                'coord': (lat2, lon2),
                'distance': distance,
                'rise': rise,
                'fall': fall,
            })
        except Exception as e:
            print(f"Error al procesar ({lat2}, {lon2}): {e}")
            continue  # Si ocurre un error, continuar con la siguiente iteración

    # Verificar si se recopilaron datos
    if not data:
#        print(" No se encontraron edificios cercanos.")
        return
    
    # Convertir la lista de datos a un DataFrame antes de exportar
    data_df = pd.DataFrame(data)
    
    # Ordenar por distancia, si aplica
    if 'distance' in data_df.columns:
        data_df = data_df.sort_values(by='distance', ascending=True)
    
    # Guardar el archivo CSV
    try:
        data_df.to_csv(output_path, index=False)
    except Exception as e:
        print(f"Error al guardar el archivo CSV: {e}")

def read_doc(doc_name, doc_type, area, distritos, data=None):
    if doc_type == '.csv':
        if doc_name == 'df_viviendas' or doc_name == 'df_ref_opt':
            type = 1
        else:
            type = 0
        try:
            output = pd.read_csv(data_path / (doc_name + doc_type))
            print(f'{doc_name + doc_type} readed.')
        except Exception as e:
            output = obtener_dataframe_direcciones(data, distritos, type)
            output.to_csv(data_path / (doc_name + doc_type), index=False)
    else:
        # Para tipos de documentos distintos a .csv (e.g., archivos de red)
        try:
            output = ox.load_graphml(data_path / (doc_name + doc_type))
            print(f'{doc_name + doc_type} readed.')
        except Exception as e:
            print(f'Cargando geodatos de {area} de calles:')
            output = ox.graph_from_place(area, network_type='walk')
            elevation_data = srtm.get_data()
            for node, data in output.nodes(data=True):
                lat = data['y']
                lon = data['x']
                elevation = elevation_data.get_elevation(lat, lon, approximate=True)  # Elevación en metros
                data['elevation'] = elevation
            ox.elevation.add_edge_grades(output, add_absolute=True)
            ox.save_graphml(output, data_path / (doc_name + doc_type))
    return output

def convertir_fecha(fecha_str, año):
    """Convierte una cadena de fecha a un objeto datetime con el año ajustado."""
    dia, mes = fecha_str.split('-')
    mes_ingles = meses_espanol_a_ingles.get(mes.lower(), mes)
    return datetime.strptime(f"{dia}-{mes_ingles}-{año}", '%d-%b-%Y')

def esta_abierto(nombre_edificio, fecha_y_hora):
    """Verifica si un edificio está abierto en un momento dado."""
    if nombre_edificio in ref_ext:
        return True
    
    año_actual = fecha_y_hora.year
    dia_semana = fecha_y_hora.strftime('%A')[:2]
    hora_actual = fecha_y_hora.time()
    horarios_edificio = horarios.get(nombre_edificio, [])
    
    for periodo in horarios_edificio:
        inicio = convertir_fecha(periodo['inicio'], año_actual)
        fin = convertir_fecha(periodo['fin'], año_actual)
        fecha_actual = convertir_fecha(f"{fecha_y_hora.day}-{fecha_y_hora.strftime('%b').lower()}", año_actual)
        
        fin_de_año = convertir_fecha("31-dic", año_actual)

        if fin < inicio:
            if inicio <= fecha_actual <= fin_de_año:
                fecha_actual = convertir_fecha(f"{fecha_y_hora.day}-{fecha_y_hora.strftime('%b').lower()}", año_actual-1)
            inicio = convertir_fecha(periodo['fin'], año_actual - 1)
        
        if inicio <= fecha_actual <= fin and dia_semana in periodo:
            for franja in periodo[dia_semana]:
                horario_apertura, horario_cierre = [datetime.strptime(h, '%H:%M').time() for h in franja]
                if horario_apertura <= hora_actual <= horario_cierre:
                    return True
    return False

def filtrar_por_distancia(df, limite=300):
    # Filtrar el DataFrame según el criterio de la columna 'distance'
    df_filtrado = df[df['distance'] <= limite]
    return df_filtrado

def shelters_hour(df_ref_int, hour_list, results_path):
    if not os.path.exists(f'{results_path}/open_shelters_by_day_and_hour_{len(hour_list)}.csv'):
        # Crear un diccionario para almacenar los datos
        shelters_by_day_hour = {}

        # Iterar sobre la lista de horas
        for current_time in tqdm(hour_list, desc=f'Creating open_shelters_by_day_and_hour.csv'):
            day = current_time.strftime('%Y-%m-%d')
            hour = current_time.strftime('%H:%M:%S')
            
            # Crear DataFrame temporal para los refugios abiertos
            open_ref_int = pd.DataFrame(columns=['name', 'osm_id', 'geometry', 'lat', 'lon', 'index_right', 'subarea'])
            for _, row in df_ref_int.iterrows():
                if esta_abierto(row['name'], current_time):
                    row_df = pd.DataFrame([row])
                    open_ref_int = pd.concat([open_ref_int, row_df], axis=0) if not open_ref_int.empty else row_df

            # Contar refugios abiertos para la hora actual
            if day not in shelters_by_day_hour:
                shelters_by_day_hour[day] = [0] * 24  # Inicializar con 24 horas
            shelters_by_day_hour[day][int(current_time.hour)] = len(open_ref_int)
            
        # Convertir a DataFrame
        df_final = pd.DataFrame(shelters_by_day_hour)
        df_final.index = [f'{hour}:00' for hour in range(24)]  # Etiquetas de filas por hora

        # Guardar en CSV
        df_final.to_csv(f'{results_path}/open_shelters_by_day_and_hour_{len(hour_list)}.csv')
    else:
        print(f'open_shelters_by_day_and_hour.csv already created.')

def process_data(hour_list, df_ref_int, buildings, distances_path, max_distance):
    '''
    buildings: nombres de los edificios guardados en la carpeta dada
    ''' 
    if not os.path.exists(f'{results_path}/point_list_{len(hour_list)}_finished.csv'):
        list_open_ref_int = {}
        if os.path.exists(f'{results_path}/point_list_{len(hour_list)}.csv'):
            point_list = pd.read_csv(f'{results_path}/point_list_{len(hour_list)}.csv')
            calculated_hour_list = sorted(point_list['time'].drop_duplicates())
        else:
            calculated_hour_list = []
        
        for time, current_time in tqdm(enumerate(hour_list), total=len(hour_list), desc=f'Processing each hour: '):
            actual_point_list = pd.DataFrame(columns=['osmid', 'type','time', 'points', 'buildings'])
            
            if current_time.strftime('%Y-%m-%d %H:%M:%S') in calculated_hour_list:
                continue
            # Crear un DataFrame vacío
            open_ref_int = pd.DataFrame(columns=['name', 'osm_id', 'geometry', 'lat', 'lon', 'index_right', 'subarea'])
            # Iterar por cada fila en df_ref_int
            for _, row in df_ref_int.iterrows():
                if esta_abierto(row['name'], current_time):
                    row_df = pd.DataFrame([row])
                    if not open_ref_int.empty:
                        open_ref_int = pd.concat([open_ref_int, row_df], axis=0)
                    else:
                        open_ref_int = row_df.copy()
            
            open_ref_int = open_ref_int.reset_index(drop=True)

            if open_ref_int.empty:
                open_ref_int_data = 'None'
            else:
                open_ref_int_data = ';'.join(open_ref_int['osm_id'])
            
            if open_ref_int_data in list_open_ref_int:
                actual_point_list = list_open_ref_int[open_ref_int_data]
                actual_point_list["time"] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                point_list = pd.concat([point_list, actual_point_list], ignore_index=True)
                point_list.to_csv(f'{results_path}/point_list_{len(hour_list)}.csv', index=False)
                continue
            
            list_buildings_considered = []
            
            for build in buildings:
                df_considered = pd.DataFrame()  # Inicializar como DataFrame vacío
                shelter_types = ['_existing.csv', '_feasible.csv'] if not open_ref_int.empty else ['_feasible.csv']
                
                for shelter_type in shelter_types:
                    try:
                        # Cargar y filtrar el archivo correspondiente
                        df_considered = pd.read_csv(f'{distances_path}/{build}{shelter_type}')
                        df_considered = filtrar_por_distancia(df_considered, max_distance)
                        
                        # Si open_ref_int no está vacío, filtrar por 'osm_id'
                        if not open_ref_int.empty and shelter_type == '_existing.csv':
                            df_considered = df_considered[df_considered['osmid'].isin(open_ref_int['osm_id'])].reset_index(drop=True)
                        
                        # Si el DataFrame no está vacío, sal del bucle
                        if not df_considered.empty:
                            break
                    except Exception as e:
                        df_considered = pd.DataFrame()  # Mantenerlo vacío en caso de error

                if df_considered.empty:
                    continue
                
                buildin_names = df_considered.loc[:, 'osmid']
                subarea_names = df_considered.loc[:, 'territory']
                list_buildings_considered.extend(buildin_names.tolist())
                
                for b, b_name in enumerate(buildin_names):                   
                    # Verificar si ya existe un registro con el mismo 'osmid' y 'time'
                    existing_row = actual_point_list[(actual_point_list['osmid'] == b_name) & (actual_point_list['time'] == current_time.strftime('%Y-%m-%d %H:%M:%S'))]
                    try:
                        subarea_name = subarea_names[b]
                    except Exception:
                        subarea_name= 'NaN'
                    
                    if existing_row.empty:
                        # Si no existe, agregar una nueva fila
                        actual_point_list = pd.concat([
                            actual_point_list,
                            pd.DataFrame({'osmid': [b_name], 
                                        'subarea': [subarea_name], 
                                        'type': shelter_type[1:-4], 
                                        'time': [current_time.strftime('%Y-%m-%d %H:%M:%S')], 
                                        'points': [1], 
                                        'buildings': [[build]]})
                        ], ignore_index=True)
                    else:
                        # Si existe, actualizar los puntos usando .loc[]
                        index = existing_row.index[0]  # Obtener el índice de la fila existente
                        actual_point_list.loc[index, 'points'] += 1
                        actual_point_list.loc[index, 'buildings'] ==  actual_point_list.loc[index, 'buildings'].append(build)
                        
            list_open_ref_int[open_ref_int_data] = actual_point_list
            if not 'point_list' in locals():
                point_list = actual_point_list.copy()
            else:            
                point_list = pd.concat([point_list, actual_point_list], ignore_index=True)
            point_list.to_csv(f'{results_path}/point_list_{len(hour_list)}.csv', index=False)
        point_list.to_csv(f'{results_path}/point_list_{len(hour_list)}_finished.csv', index=False) 
        point_list['buildings'] = point_list['buildings'].apply(str)
    else:
        print(f'Reading df_point_list ...')
        point_list = pd.read_csv(f'{results_path}/point_list_{len(hour_list)}_finished.csv')
        print(f'    [Done]')    
    return point_list

def listar_buildings_por_numero(carpeta):
    # Verifica si la carpeta existe
    if not os.path.exists(carpeta):
        print(f"La carpeta '{carpeta}' no existe.")
        return []
        
    # Lista los archivos .csv
    archivos_csv = [archivo for archivo in os.listdir(carpeta) if archivo.endswith('.csv')]
        
    # Procesa los nombres de archivos para quedarse solo con 'building_149'
    buildings = []
    for archivo in archivos_csv:
        if archivo.startswith("building_") and ('_feasible' in archivo or '_existing' in archivo):
            # Extrae la parte antes del primer '_feasible' o '_existing'
            building_id = archivo.split('_feasible')[0].split('_existing')[0]
            buildings.append(building_id)
        
    # Elimina duplicados y ordena por número
    return sorted(set(buildings), key=lambda x: int(x.split('_')[1]))

def fitness_list_creation(hour_list):
    if not os.path.exists(f'{results_path}/df_fitness.csv'):
        df_fitness = pd.DataFrame(columns=['hour', 'fitness'])
        
        for current_time in tqdm(hour_list, desc='fitness stuff: '):
            fitness = point_list.loc[(point_list['type'] == 'feasible')&(point_list['time'] == current_time.strftime('%Y-%m-%d %H:%M:%S')), 'points'].sum()
            df_fitness = pd.concat([
                            df_fitness,
                            pd.DataFrame({'hour': [current_time.strftime('%Y-%m-%d %H:%M:%S')], 'fitness': fitness})
                        ], ignore_index=True)
            
        df_fitness.to_csv(f'{results_path}/df_fitness.csv', index=False)
    else:
        print(f'Reading df_fitness ...')
        df_fitness = pd.read_csv(f'{results_path}/df_fitness.csv')
        print(f'    [Done]')
    return df_fitness

def optimization(hour_list, point_list):
    if not os.path.exists(f'{results_path}/df_optimization.csv'):
        for current_time in tqdm(hour_list, desc=f'Optimizing hours: '):
            rows = point_list[point_list['time'] == current_time.strftime('%Y-%m-%d %H:%M:%S')]
            new_rows = rows.copy()        
            new_rows['buildings'] = new_rows['buildings'].apply(ast.literal_eval)
            for index in new_rows['osmid']:
                new_rows.sort_values(by='points', ascending=False, inplace=True)
                new_rows.reset_index(drop=True, inplace=True)
                if new_rows['points'][0] == 0:
                    break
                supplied_buildings = new_rows.iloc[0]['buildings']
                help_independent = rows[rows['osmid'] == new_rows.iloc[0]['osmid']]['points'].values[0]
                new_row_optimization = pd.DataFrame({'time': [new_rows['time'][0]],
                                                    'osmid': [new_rows['osmid'][0]],
                                                    'subarea': [new_rows.get('subarea', np.nan)[0]],
                                                    'help_convined': [new_rows['points'][0]],
                                                    'help_independent': [help_independent],
                                                    }) 
                if 'df_optimization' not in locals():
                    df_optimization = new_row_optimization.copy()   
                else:
                    df_optimization = pd.concat([df_optimization, new_row_optimization], ignore_index=True)

                new_rows['buildings'] = new_rows['buildings'].apply(lambda x: [item for item in x if item not in supplied_buildings])
                new_rows['points'] = new_rows['buildings'].apply(len)
                
        df_optimization.to_csv(f'{results_path}/df_optimization.csv', index=False)
    else:
        print(f'Reading df_optimization ...')
        df_optimization = pd.read_csv(f'{results_path}/df_optimization.csv')
        print(f'    [Done]') 
    return df_optimization

def process_and_save_dataframes(df_optimization, results_path):
    # Verificar si la columna 'time' ya está en formato datetime
    if not pd.api.types.is_datetime64_any_dtype(df_optimization['time']):
        df_optimization['time'] = pd.to_datetime(df_optimization['time'])

    def reorder_and_save(df, doc_name):        
        df = df.sort_values(
            by=[doc_name, 'hour_of_day', 'help_convined', 'help_independent'], 
            ascending=[True, True, False, False]
        )
        df['rank'] = df.groupby(['hour_of_day','subarea', doc_name]).cumcount() + 1
        
        df = df.merge(
            df_ref_opt[['osm_id', 'building_type_name']],  # Seleccionamos columnas necesarias
            left_on='osmid',  # Columna del DataFrame original
            right_on='osm_id',  # Columna del DataFrame de referencia
            how='left'  # Realizamos un left join para mantener todas las filas de df
        )

        # Si no necesitas 'osm_id' del merge, puedes eliminarla
        df = df.drop(columns=['osm_id'])
                    
        output_name = f"{results_path}/{doc_name}_summary.csv"
        
        df.to_csv(output_name, index=False)

    # 1. Sumar por día
    df_daily = df_optimization.groupby(
        [df_optimization['time'].dt.floor('D'),
         df_optimization['time'].dt.hour.rename('hour_of_day'), 
        'osmid',
        'subarea'
    ]).agg({
        'help_convined': 'sum',
        'help_independent': 'sum'
    }).reset_index()
    df_daily.rename(columns={'time': 'date'}, inplace=True)
    
    reorder_and_save(df_daily, 'date')

    # 2. Sumar por semana, desglosado por hora
    df_weekly = df_optimization.groupby([
        df_optimization['time'].dt.isocalendar().week.rename('week_of_year'),
        df_optimization['time'].dt.hour.rename('hour_of_day'),
        'osmid',
        'subarea'
    ]).agg({
        'help_convined': 'sum',
        'help_independent': 'sum'
    }).reset_index()
    
    reorder_and_save(df_weekly, 'week_of_year')

    # 3. Sumar por mes, desglosado por hora
    df_monthly = df_optimization.groupby([
        df_optimization['time'].dt.month.rename('month_of_year'),
        df_optimization['time'].dt.hour.rename('hour_of_day'),
        'osmid',
        'subarea'
    ]).agg({
        'help_convined': 'sum',
        'help_independent': 'sum'
    }).reset_index()
    
    reorder_and_save(df_monthly, 'month_of_year')

    # 4. Sumar por estación climática (asumiendo estaciones del hemisferio norte), desglosado por hora
    seasons = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    }

    df_optimization['season'] = df_optimization['time'].dt.month.map(seasons)
    df_seasonal = df_optimization.groupby([
        'season',
        df_optimization['time'].dt.hour.rename('hour_of_day'),
        'osmid',
        'subarea'
    ]).agg({
        'help_convined': 'sum',
        'help_independent': 'sum'
    }).reset_index()
    
    reorder_and_save(df_seasonal, 'season')

    # 5. Sumar por año, desglosado por hora
    df_yearly = df_optimization.groupby([
        df_optimization['time'].dt.year.rename('year'),
        df_optimization['time'].dt.hour.rename('hour_of_day'),
        'osmid',
        'subarea'
    ]).agg({
        'help_convined': 'sum',
        'help_independent': 'sum'
    }).reset_index()
    
    reorder_and_save(df_yearly, 'year')

if __name__ == "__main__":
    ciudad = "Bilbao"
    year = 2024
    max_distance = 300
    
    distritos = ["Deusto", "Uribarri", "Otxarkoaga-Txurdinaga", "Begona", "Ibaiondo", "Abando", "Errekalde", "Basurtu-Zorrotza"]
    main_path = Path(__file__).resolve().parent.parent   
    data_path = main_path / f'Data/{ciudad}'
    results_path = main_path / f'Results/{ciudad}'
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    if not os.path.exists(results_path):
        os.makedirs(results_path)
        
    docs_to_read = [['df_viviendas','.csv', [ciudad, building]], ['df_ref_int', '.csv', list(horarios.keys())], ['df_ref_opt', '.csv', [ciudad, poss_ref]], ['walk', '.graphml', None]]
    docs = [read_doc(name, ext, ciudad, distritos, data) for name, ext, data in docs_to_read]
    df_viviendas, df_ref_int, df_ref_opt, G = docs
    
    if not os.path.exists(f'{str(data_path)}/Buildings Distances'):
            os.makedirs(f'{str(data_path)}/Buildings Distances')
    
    
    
    
    for building_residential in tqdm(df_viviendas.itertuples(index=False), desc='Reading buildings docs: ', total=len(df_viviendas)):
        # Nombre del archivo "existing"
        file_name_existing = f"{building_residential.name}_existing.csv"
        input_path_existing = f'{str(data_path)}/Buildings Distances/{file_name_existing}'
        
        if not os.path.exists(input_path_existing):
            obtener_edificios_mas_cercanos(building_residential, df_ref_int, G, input_path_existing)
        
        # Nombre del archivo "feasible"
        file_name_feasible = f"{building_residential.name}_feasible.csv"
        input_path_feasible = f'{str(data_path)}/Buildings Distances/{file_name_feasible}'
        
        if not os.path.exists(input_path_feasible):
            obtener_edificios_mas_cercanos(building_residential, df_ref_opt, G, input_path_feasible)

    distances_path = f'{str(data_path)}/Buildings Distances'
    
    buildings = listar_buildings_por_numero(distances_path)

    # Definir la primera y última fecha del año
    start_date = datetime(year, 8, 12, 0, 0)
    end_date = datetime(year, 8, 18, 23, 0)
    hour_list = [start_date + timedelta(hours=i) for i in range(int((end_date - start_date).total_seconds() / 3600) + 1)]
    
    shelters_hour(df_ref_int, hour_list, results_path)
    
    point_list = process_data(hour_list, df_ref_int, buildings, distances_path, max_distance)
    
    df_fitness = fitness_list_creation(hour_list)
    
    point_list_filtered = point_list[point_list['type'] != 'existing'].reset_index(drop=True)
    point_list_filtered.to_csv(f'{results_path}/point_list_filtered.csv')
    
    df_optimization = optimization(hour_list, point_list_filtered)
    
    process_and_save_dataframes(df_optimization, results_path)
    
    print(f'Se han guardado los datos en la carpeta de resultados de {ciudad}')