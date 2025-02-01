import os
import re
import ast
import srtm
import numpy as np
import osmnx as ox
import pandas as pd
from tqdm import tqdm
import networkx as nx
import geopandas as gpd

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

def obtener_geometrias(osmid_list):
    data = get_osm_elements(osmid_list[0], osmid_list[1])
    return data

def obtener_dataframe_direcciones(data): 
    """Obtiene un DataFrame con las coordenadas de cada dirección y asigna un 'Territorio' (distrito)."""
    print('Procesando datos...')

    refug_data = obtener_geometrias(data)
    df_refug_data = pd.DataFrame(refug_data)
    gdf_refug_data = gpd.GeoDataFrame(df_refug_data, geometry='geometry')
    gdf_refug_data.set_crs("EPSG:4326", inplace=True)
    
    return gdf_refug_data

def obtener_edificios_mas_cercanos(df1, df2, G, output_path,max_distance):
    """
    Obtiene una lista con los nombres de los edificios más cercanos y la distancia caminada
    desde cada edificio en df1 a los edificios en df2.
    """
    if df2.empty:
#        print("El DataFrame df2 está vacío. No se realizará ningún cálculo.")
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
        if euc_dist > max_distance:  # Filtrar por distancia máxima
            continue

        try:
            # Encuentra el nodo más cercano en G
            nodo_df2 = ox.distance.nearest_nodes(G, lon2, lat2)

            # Encuentra la ruta más corta entre nodo_df1 y nodo_df2
            route = ox.shortest_path(G, nodo_df1, nodo_df2, weight='length')
            distance = nx.path_weight(G, route, weight="length")
            if distance > max_distance:
                continue
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
        
def read_doc(data_path, doc_name, doc_type, city, data=None):
    if doc_type == '.csv':
        try:
            output = pd.read_csv(data_path / (doc_name + doc_type))
            print(f'{doc_name + doc_type} readed.')
        except Exception as e:
            output = obtener_dataframe_direcciones(data)
            output.to_csv(data_path / (doc_name + doc_type), index=False)
    else:
        # Para tipos de documentos distintos a .csv (e.g., archivos de red)
        try:
            output = ox.load_graphml(data_path / (doc_name + doc_type))
            print(f'{doc_name + doc_type} readed.')
        except Exception as e:
            print(f'Cargando geodatos de {city} de calles:')
            output = ox.graph_from_place(city, network_type='walk')
            elevation_data = srtm.get_data()
            for node, data in output.nodes(data=True):
                lat = data['y']
                lon = data['x']
                elevation = elevation_data.get_elevation(lat, lon, approximate=True)  # Elevación en metros
                data['elevation'] = elevation
            ox.elevation.add_edge_grades(output, add_absolute=True)
            ox.save_graphml(output, data_path / (doc_name + doc_type))
    return output

def filtrar_por_distancia(df, max_distance):
    # Filtrar el DataFrame según el criterio de la columna 'distance'
    df_filtrado = df[df['distance'] <= max_distance]
    return df_filtrado

def process_data(hour_list, buildings, distances_path, max_distance, results_path):
    '''
    buildings: nombres de los edificios guardados en la carpeta dada
    ''' 
    if not os.path.exists(f'{results_path}/point_list_{len(hour_list)}_finished.csv'):
        if os.path.exists(f'{results_path}/point_list_{len(hour_list)}.csv'):
            point_list = pd.read_csv(f'{results_path}/point_list_{len(hour_list)}.csv')
        
        for time, current_time in tqdm(enumerate(hour_list), total=len(hour_list), desc=f'Processing each hour: '):
            actual_point_list = pd.DataFrame(columns=['osmid', 'type','time', 'points', 'buildings'])
            
            list_buildings_considered = []
            
            for build in buildings:
                df_considered = pd.DataFrame()  # Inicializar como DataFrame vacío
                shelter_type = '_feasible.csv'
                try:
                    # Cargar y filtrar el archivo correspondiente
                    df_considered = pd.read_csv(f'{distances_path}/{build}{shelter_type}')
                    df_considered = filtrar_por_distancia(df_considered, max_distance)
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

def optimization(hour_list, point_list, results_path):
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
                                                    'help_independent': [help_independent]}) 
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

def process_and_save_dataframes(df_optimization, results_path, city, hour_list):
    # Verificar si la columna 'time' ya está en formato datetime
    if not pd.api.types.is_datetime64_any_dtype(df_optimization['time']):
        df_optimization['time'] = pd.to_datetime(df_optimization['time'])

    def reorder_and_save(df, doc_name, city):        
        df = df.sort_values(
            by=[doc_name, 'hour_of_day', 'help_convined', 'help_independent'], 
            ascending=[True, True, False, False]
        )
        df['rank'] = df.groupby(['hour_of_day','subarea', doc_name]).cumcount() + 1
                    
        output_name = f"{results_path}/{city}.csv"
        
        df.to_csv(output_name, index=False)

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
    
    reorder_and_save(df_daily, 'date', city)
    
    files_to_delete = [
        f'{results_path}/df_optimization.csv',
        f'{results_path}/point_list_{len(hour_list)}_finished.csv',
        f'{results_path}/point_list_{len(hour_list)}.csv']

    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)

def get_max_existing_building(data_path):
    """Encuentra el número más alto en los archivos existentes con formato *_feasible.csv."""
    max_number = -1
    pattern = re.compile(r'(\d+)_feasible\.csv$')
    
    distances_path = f'{str(data_path)}/Buildings Distances'
    if not os.path.exists(distances_path):
        return max_number
    
    for file in os.listdir(distances_path):
        match = pattern.search(file)
        if match:
            num = int(match.group(1))
            max_number = max(max_number, num)
    
    return max_number



def process_city(city, main_path, results_path, hour_list, max_distance):
    result_file = results_path / f"{city}.csv"
    if result_file.exists():
        print(f'Analysis for {city} done.')
        return
    
    data_path = main_path / f'Data/{city}'
    os.makedirs(data_path, exist_ok=True)
    
    # Lectura de documentos
    docs_to_read = [
        ['df_residences', '.csv', [city, "building"]],
        ['df_feasible_shelters', '.csv', [city, "poss_ref"]],
        ['walk', '.graphml', None]
    ]
    df_residences, df_feasible_shelters, G = [read_doc(data_path, doc_name, doc_type, city, data) for doc_name, doc_type, data in docs_to_read]
    
    # Crear directorio si no existe
    buildings_distances_path = data_path / 'Buildings Distances'
    os.makedirs(buildings_distances_path, exist_ok=True)
    
    # Obtener el archivo con el número más alto existente
    max_existing = get_max_existing_building(data_path)

    # Iterar sobre los edificios comenzando desde el más alto existente
    for building_residential in tqdm(df_residences.itertuples(index=False), desc='Reading buildings docs: ', total=len(df_residences)):
        try:
            building_number = int(re.search(r'\d+', building_residential.name).group())
        except AttributeError:
            continue  # Saltar si no hay número en el nombre

        if building_number <= max_existing:
            continue  # Saltar si ya se ha procesado
        
        file_name_feasible = f"{building_residential.name}_feasible.csv"
        input_path_feasible = buildings_distances_path / file_name_feasible
        
        if not input_path_feasible.exists():
            obtener_edificios_mas_cercanos(building_residential, df_feasible_shelters, G, str(input_path_feasible), max_distance)
    
    # Procesamiento posterior
    buildings = listar_buildings_por_numero(str(buildings_distances_path))    
    point_list = process_data(hour_list, buildings, str(buildings_distances_path), max_distance, results_path)
    df_optimization = optimization(hour_list, point_list, results_path)
    
    process_and_save_dataframes(df_optimization, results_path, city, hour_list)
    
    print(f'Analysis for {city} done.')