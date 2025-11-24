import osmnx as ox
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


def main():
    # ------------------------------------------------------------------
    # 0. Diccionario de IDs de OSM
    # ------------------------------------------------------------------
    # Definir horarios de apertura con meses en español
    dict_osmid_refug = {
        # Interior Shelters
        'Edificio San Agustin': 'W248634544',
        'Biblioteca Central de Bidebarrieta': 'W108497734',
        'Biblioteca municipal de San Ignacio': 'N10308519810', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Biblioteca Foral': 'W108504682',
        'Centro Municipal de Solokoetxe': 'W420558992',
        'Centro Mpal. de Distrito Zabala': 'N11229801356', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Biblioteca de San Francisco':'N5056088727',
        'Barrio Altamira 39': 'N5056200430',
        'Centro Mpal. de Zorroza': 'N11229807742',
        'Centro Mpal. de Distrito Basurto': 'N9607467466',
        'Centro Mpal. de Irala': 'N5056183351', #MENTIRA, pero no hay elemento creado en OSM A FECHA DE 12/11/2024
        'Oficina Municipal de Distrito Abando': 'N4731925117', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'CEPA Bilbao Uretamendi': 'W301165234',
        'Centro Mpal. de Distrito Rekalde': 'N9607455457', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Oficina Municipal de Distrito Uribarri': 'W48045715',
        'Centro Mpal. de Distrito San Ignacio': 'N5056421870', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Centro Mpal. de Castanos': 'N9607363904', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Bidarte': 'W185205681',
        'Mercado Santutxu': 'N5056328910', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Centro Municipal de Txurdinaga': 'W235157481',
        'Centro Mpal. de Distrito Begona': 'N9607391207',
        'Centro Civico Otxarkoaga': 'W164512079',
        'Polideportivo Miribilla': 'W376396126', #MENTIRA, pero no hay elemento creado en OSM A FECHA DE 12/11/2024
        'Polideportivo Abusu-La Pena': 'W397099000',
        'Polideportivo San Ignacio': 'W290069950',
        'Polideportivo Zorroza': 'W151883539',
        'Polideportivo Deusto': 'W185205688',
        'Polideportivo Artxanda': 'W162445376',
        'Polideportivo Txurdinaga': 'W305622069',
        'Polideportivo El Fango': 'W41415573',
        'Mercado de Labayru': 'N5056184623', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Mercado de Deusto': 'N4254043797', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Mercado de la Ribera': 'N5056437799', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Mercado de San Ignacio': 'N5056355015', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Mercado de Trauko': 'N5056356248',
        'Mercado del Ensanche': 'W41688628',
        'Mercado de Otxarkoaga': 'W164510985',
        'Oficina de Turismo': 'W110895854',
        'Bilbao-Arte': 'W375390416',
        'Sala BBK': 'N3207631929', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Azkuna Zentroa - Alhondiga Bilbao': 'W96337695',
        'Archivo Historico': 'N4761972760',
        'Museo Bellas Artes de Bilbao': 'W28211432',
        'Museo de Reproducciones Artisticas': 'W404432093',
        'Itsasmuseum Bilbao': 'N518227646', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Estacion del Funicular (arriba)': 'W123440625',
        'Estacion del Funicular (abajo)': 'W123440604',
        'Bilbao Intermodal': 'W632988668',
        'Estacion de Abando Indalecio Prieto': 'W28776478',
        'Estacion Tren Hospital Basurto': 'W388248471', 
        'Estacion Tren Amezola': 'W111740255',
        'Bilbao La Concordia': 'W44113519',
        'Estacion Tren Autonomia': 'N5056379164',
        'Estacion Tren San Mames': 'W163195554',
        'Estacion de Euskotren Matico': 'N5056353256',
        'Estacion de Euskotren Uribarri': 'N4508853267', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Estacion de Euskotren Zazpi Kaleak': 'W485363913',
        'Estacion de Euskotren Zurbaranbarri': 'N4060532227', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Estacion de Euskotren Txurdinaga': 'N4060532216', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Entrada metro Langaran': 'N4060532217', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Entrada metro Plaza Kepa Enbeitia': 'N4060532220', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Parroquia Santos Juanes': 'W41525574',
        'Iglesia de Santa Ana y San Nicolas de Bari': 'W163196945',
        'Sala Ondare Aretoa': 'N4762096882', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'Rekalde aretoa': 'N1271964866', #SIN GEOMETRIA A FECHA DE 12/11/2024
        'El Corte Ingles': 'W44016098',
        'Centro Comercial Zubiarte': 'W171882527',
        
        # Exterior Shelters
        'Altamira':'W297437906', #Se ha tomado un parque                                    
        'Artxanda': 'R2173101', #Se ha tomado un parque                               
        'Parque San Antonio de Iturrigorri': 'W387150941',
        'Kobetamendi': 'W118382826',
        'Parque de Larreagaburu': 'W41385026',
        'Santa Ana': 'W302301657',
        'Sarrikue':'W616359838', #Se ha tomado unas huertas                             
        'Gana parkea':'W396313608',
        'Armulaza y Maspilza': 'W389201093', #Se ha tomado una zona de mina             
        'Arnotegui': 'W757726115', #Se ha tomado un parque                              
        'Arraiz': 'W607046510',
        'Artigas': 'W607046533', #Se ha tomado un restaurante                           
        'Avril': 'W815568777', #Se ha tomado un area de picnic                          
        'Pagasarri': 'W618595105', #Una aproximacion muy regulera                       
        'Santo Domingo': 'W616902875',
        'Parque Botica Vieja - Botikazar': 'R2915183',
        'Lezeaga': 'W604587407',
        'Parque de Ametzola': 'W35098990',
        'Parque de Bidarte': 'W185205697',
        'Parque de Doña Casilda de Iturrizar': 'W28192022',
        'Parque de Etxebarria': 'W28503540',                                            
        'Parque de Eskurtze': 'R17902368',                                              
        'Parque de Europa': 'W39021466',
        'Parque Uretamendi': 'R17320677',
        'Parque de Ibaieder': 'W98170639',
        'Jardines de Gernika': 'W41415866',
        'Parque Encarnación': 'W165888799',
        'Parque de Miribilla': 'W41415864',
        'Larreagaburu parkea': 'W41385159',
        'Abandoibarra parkea': 'W174088320',
        'Muelle Evaristo Churruca': 'W174088298',                                       
        'Parque de Sarriko': 'W46927920',
        'Paseo de Santa Mónica': 'W550631831',                                          
        'Guggenheim parkea': 'W174783496',
        'Jardines de Iparralde': 'W431693191',
        'Jardines Emiliano Arriaga': 'W41414906',
        'Parque El Arenal': 'W28225532',
        'Parque de Zorroza - Zazpilanda': 'W396313609',
        'Plaza Arbidea': 'W201506103',
        'Plaza Azoka': 'W386765838',
        'Plaza Basurtugorta': 'W667667737',
        'Calle Ondarroa': 'W128191927', #Un poco inventado                              
        'Plaza de la Casilla': 'W35098989',
        'Plaza Eugenio Olabarrieta': 'W365613896',
        'Plaza Euskadi': 'W174088300',
        'Plaza Calisto Diez': 'W111741268',
        'Plaza Indautxu': 'W174482547',
        'Plaza Jose Maria Makua': 'W585581598',
        'Plaza La Salve': 'W183190861',
        'Plaza San Juan XXIII': 'W417899333',
        'Plaza San Pedro': 'W248688329',
        'Saralegui': 'W108498126',
        'Plaza Baztan': 'W290069947',
        'Plaza Zabalburu_a': 'W196742063',
        'Plaza Zabalburu_b':'W312861704',
        'Campa de Basarrate': 'W41384146',
        'Jardines de Albia': 'W28225493',
        'Jardines de Garai': 'R240087',
        'Jardines Xalbador': 'W448328349',
        'Guggenheim Chorros de agua': 'W431641215',
        'Iglesia San Vicente portico': 'W28757167', #Un poco inventado
        'Calle Maestro Damian Gonzalez (la Pinza)': 'W224294812', #Un poco inventado    
        'Paseo Puente del Arenal': 'W413679792',
        'Plaza Nueva': 'W41789694', #Un poco inventado
        'Puente Ayuntamiento (Ripa)': 'W419919866',
        'Puente de Deusto (Abandoibarra)': 'W419919871',
        'Puente Euskalduna (Deusto)': 'W569086628',
        'Puente Pedro Arrupe (Abandoibarra)': 'R16998640',
    }

    place_name = "Bilbao, Spain"

    print("======================================================")
    print("  Mancha 300 m + red peatonal + límite Bilbao (OSM)")
    print("======================================================\n")

    # ------------------------------------------------------------------
    # 1. Preparar DataFrame de IDs
    # ------------------------------------------------------------------
    n_total = len(dict_osmid_refug)
    print(f"Paso 1/6: preparando listas de OSM IDs ({n_total} elementos)...")

    df_labels = pd.DataFrame(
        {
            "name_custom": list(dict_osmid_refug.keys()),
            "osm_id": [int(v[1:]) for v in dict_osmid_refug.values()],
            "osmid_str": list(dict_osmid_refug.values()),
        }
    )

    # ------------------------------------------------------------------
    # 2. Refugios desde OSM (una sola llamada)
    # ------------------------------------------------------------------
    print("\nPaso 2/6: consultando geometrías de refugios en OSM (llamada masiva)...\n")

    try:
        gdf = ox.geocode_to_gdf(df_labels["osmid_str"].tolist(), by_osmid=True)
    except Exception as e:
        print("\n*** ERROR al consultar OSM para los refugios ***")
        print(e)
        return

    # Asegurar columna osm_id
    if "osm_id" not in gdf.columns:
        if "osmid" in gdf.columns:
            gdf = gdf.rename(columns={"osmid": "osm_id"})
        else:
            print("No encuentro columna osm_id/osmid en gdf. Columnas:")
            print(list(gdf.columns))
            return

    # Hacemos right-merge para quedarnos sólo con tus IDs
    gdf = gdf.merge(df_labels[["osm_id"]], on="osm_id", how="right")
    gdf = gdf[~gdf.geometry.isna()].copy()

    print(f"  -> Geometrías de refugios con éxito: {len(gdf)}")

    if gdf.empty:
        print("No queda ninguna geometría válida de refugios. Fin.")
        return

    # ------------------------------------------------------------------
    # 3. Proyección + buffer 300 m + disolver
    # ------------------------------------------------------------------
    print("\nPaso 3/6: proyectando refugios y creando buffers de 300 m...")

    try:
        gdf_proj = gdf.to_crs(epsg=25830)
        print("  -> Proyección de refugios a EPSG:25830 correcta.")
    except Exception as e:
        print("  -> No se ha podido proyectar refugios. Error:")
        print("     ", e)
        print("     Los 300 serán en unidades del CRS original (no metros).")
        gdf_proj = gdf

    print("  -> Creando buffers de 300 m...")
    gdf_buffer = gdf_proj.copy()
    gdf_buffer["geometry"] = gdf_buffer.geometry.buffer(300)

    print("  -> Disolviendo solapes de buffers...")
    union_geom = gdf_buffer.unary_union
    gdf_union = gpd.GeoDataFrame(geometry=[union_geom], crs=gdf_proj.crs)

    # ------------------------------------------------------------------
    # 4. Límite administrativo de Bilbao
    # ------------------------------------------------------------------
    print("\nPaso 4/6: descargando límite administrativo de Bilbao...")

    try:
        gdf_bilbao = ox.geocode_to_gdf(place_name)
    except Exception as e:
        print("\n*** ERROR al obtener el límite de Bilbao ***")
        print(e)
        return

    try:
        gdf_bilbao_proj = gdf_bilbao.to_crs(epsg=25830)
        print("  -> Límite de Bilbao reproyectado a EPSG:25830.")
    except Exception as e:
        print("  -> No se ha podido proyectar el límite de Bilbao. Error:")
        print("     ", e)
        gdf_bilbao_proj = gdf_bilbao

    # ------------------------------------------------------------------
    # 5. Red peatonal de Bilbao
    # ------------------------------------------------------------------
    print("\nPaso 5/6: descargando red peatonal de Bilbao (network_type='walk')...")

    try:
        G_walk = ox.graph_from_place(place_name, network_type="walk", simplify=True)
    except Exception as e:
        print("\n*** ERROR al obtener la red peatonal ***")
        print(e)
        return

    # Pasamos el grafo a GeoDataFrames (sólo edges)
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G_walk, nodes=True, edges=True)

    try:
        gdf_edges_proj = gdf_edges.to_crs(epsg=25830)
        print("  -> Red peatonal reproyectada a EPSG:25830.")
    except Exception as e:
        print("  -> No se ha podido proyectar la red peatonal. Error:")
        print("     ", e)
        gdf_edges_proj = gdf_edges

    # ------------------------------------------------------------------
    # 6. Gráfica final: límite + red peatonal + mancha 300 m
    # ------------------------------------------------------------------
    print("\nPaso 6/6: generando la gráfica final...")
    print("  -> Fondo: límite Bilbao + red peatonal")
    print("  -> Encima: mancha disuelta de 300 m de refugios\n")

    fig, ax = plt.subplots(figsize=(8, 8))

    # 6.1. Límite administrativo (solo borde)
    gdf_bilbao_proj.boundary.plot(ax=ax, linewidth=1.5)

    # 6.2. Red peatonal
    gdf_edges_proj.plot(ax=ax, linewidth=0.3, alpha=0.5)

    # 6.3. Mancha disuelta de 300 m
    gdf_union.plot(ax=ax, alpha=0.4, edgecolor="black", linewidth=1.2)

    ax.set_aspect("equal")
    ax.set_axis_off()

    plt.tight_layout()
    print("Mostrando mapa...\n")
    plt.show()


if __name__ == "__main__":
    main()