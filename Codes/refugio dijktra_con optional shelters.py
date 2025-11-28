import osmnx as ox
import geopandas as gpd
import pandas as pd
import networkx as nx


def main():
    # --------------------------------------------------------------
    # 0. Refugios OUTDOOR / INDOOR (rellena con tus IDs)
    # --------------------------------------------------------------
    dict_osmid_refug_indoor = {
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
        'Centro Comercial Zubiarte': 'W171882527'}
    
    # Tags de edificio
    building_tags = {
        "building": [
            "apartments", "barracks", "bungalow", "cabin", "detached", "annexe",
            "dormitory", "farm", "house", "houseboat", "residential",
            "semidetached_house", "static_caravan", "stilt_house", "terrace",
            "trullo", "yes"
        ]
    }

    place_name = "Bilbao, Spain"
    cutoff_m = 100  # distancia en metros por la red

    print("========================================================")
    print("  Cobertura indoor/outdoor a 300 m por red peatonal")
    print("========================================================\n")

    # --------------------------------------------------------------
    # 1. Refugios OUTDOOR desde CSV + INDOOR desde diccionario
    # --------------------------------------------------------------
    print("Paso 1/5: preparando refugios OUTDOOR / INDOOR...")

    # 1.a) Refugios OUTDOOR desde CSV
    csv_path = r"C:\Users\asier.divasson\Documents\GitHub\AccessiCity\Data\_Bilbao\df_ref_opt.csv"
    try:
        df_outdoor = pd.read_csv(csv_path)
    except Exception as e:
        print("\n*** ERROR al leer el CSV de refugios OUTDOOR ***")
        print(f"Ruta: {csv_path}")
        print(e)
        return

    cols_necesarias = {"name", "building_type_name", "osm_id", "geometry", "lat", "lon", "index_right", "subarea"}
    if not cols_necesarias.issubset(df_outdoor.columns):
        print("\n*** ERROR: el CSV no contiene todas las columnas necesarias ***")
        print(f"Se esperaban al menos: {cols_necesarias}")
        print(f"Columnas encontradas: {set(df_outdoor.columns)}")
        return

    # Nos quedamos solo con filas con lat/lon válidos
    df_outdoor = df_outdoor.dropna(subset=["lat", "lon"]).copy()

    # Creamos GeoDataFrame de OUTDOOR a partir de lat/lon
    gdf_outdoor = gpd.GeoDataFrame(
        df_outdoor.copy(),
        geometry=gpd.points_from_xy(df_outdoor["lon"], df_outdoor["lat"]),
        crs="EPSG:4326"
    )
    gdf_outdoor["name_custom"] = gdf_outdoor["name"]
    # Como has dicho "en vez de dict_osmid_refug_outdoor", asumimos que todo el CSV son refugios outdoor
    gdf_outdoor["tipo"] = "outdoor"

    n_outdoor_csv = len(gdf_outdoor)
    print(f"  -> Refugios OUTDOOR desde CSV: {n_outdoor_csv}")

    # 1.b) Refugios INDOOR desde diccionario (para consultar en OSM)
    registros_indoor = []
    for nombre, osmid in dict_osmid_refug_indoor.items():
        registros_indoor.append(
            {
                "name_custom": nombre,
                "osmid_str": osmid,
                "osm_id": int(osmid[1:]),
                "tipo": "indoor",
            }
        )

    df_indoor = pd.DataFrame(registros_indoor)
    n_indoor_dic = len(df_indoor)
    print(f"  -> Refugios INDOOR desde diccionario: {n_indoor_dic}")

    if n_outdoor_csv == 0 and n_indoor_dic == 0:
        print("No hay refugios definidos (ni outdoor ni indoor). Fin.")
        return

    # --------------------------------------------------------------
    # 2. Descargar geometrías INDOOR desde OSM y red peatonal
    # --------------------------------------------------------------
    print("\nPaso 2/5: descargando geometrías de refugios INDOOR desde OSM...")

    if n_indoor_dic > 0:
        try:
            gdf_indoor_osm = ox.geocode_to_gdf(df_indoor["osmid_str"].tolist(), by_osmid=True)
        except Exception as e:
            print("\n*** ERROR al consultar OSM para los refugios INDOOR ***")
            print(e)
            return

        # Asegurar columna osm_id
        if "osm_id" not in gdf_indoor_osm.columns:
            if "osmid" in gdf_indoor_osm.columns:
                gdf_indoor_osm = gdf_indoor_osm.rename(columns={"osmid": "osm_id"})
            else:
                print("No encuentro columna osm_id/osmid en gdf_indoor_osm. Columnas:")
                print(list(gdf_indoor_osm.columns))
                return

        # Cruzamos con df_indoor para recuperar name_custom y tipo
        gdf_indoor = gdf_indoor_osm.merge(
            df_indoor[["osm_id", "name_custom", "osmid_str", "tipo"]],
            on="osm_id",
            how="left"
        )
        gdf_indoor = gdf_indoor[~gdf_indoor.geometry.isna()].copy()
    else:
        # GeoDataFrame vacío con las columnas esperadas
        gdf_indoor = gpd.GeoDataFrame(columns=["name_custom", "tipo", "geometry"], geometry="geometry", crs="EPSG:4326")

    print("  -> Refugios INDOOR descargados y procesados.")

    # Unificamos OUTDOOR (CSV) + INDOOR (OSM) en un solo GeoDataFrame
    gdf_outdoor_simple = gdf_outdoor[["name_custom", "tipo", "geometry"]].copy()
    gdf_indoor_simple = gdf_indoor[["name_custom", "tipo", "geometry"]].copy()

    gdf_refug = pd.concat([gdf_outdoor_simple, gdf_indoor_simple], ignore_index=True)
    gdf_refug = gdf_refug[~gdf_refug.geometry.isna()].copy()

    n_total_refug = len(gdf_refug)
    print(f"  -> Total refugios (outdoor + indoor) con geometría válida: {n_total_refug}")

    if gdf_refug.empty:
        print("No queda ninguna geometría válida de refugios. Fin.")
        return

    print("\n  Descargando red peatonal de Bilbao (network_type='walk')...")
    try:
        G_walk = ox.graph_from_place(place_name, network_type="walk", simplify=True)
    except Exception as e:
        print("\n*** ERROR al obtener la red peatonal ***")
        print(e)
        return

    # --------------------------------------------------------------
    # 3. Nodos cercanos a refugios y edificios
    # --------------------------------------------------------------
    print("\nPaso 3/5: pegando refugios y edificios a la red peatonal...")

    # Coordenadas de refugios (usamos centroides por si algún indoor es polígono)
    # reproyectar a CRS métrico para calcular centroides correctamente
    gdf_refug_proj = gdf_refug.to_crs(25830)
    refug_centroids_proj = gdf_refug_proj.geometry.centroid

    # volver a WGS84 (lat/lon) para nearest_nodes
    refug_centroids = gpd.GeoSeries(refug_centroids_proj, crs=25830).to_crs(4326)

    refug_x = refug_centroids.x.values
    refug_y = refug_centroids.y.values

    # Nodos de red más cercanos a cada refugio
    refug_nodes_all = ox.distance.nearest_nodes(G_walk, X=list(refug_x), Y=list(refug_y))
    gdf_refug["nearest_node"] = list(refug_nodes_all)

    # Fuentes por tipo
    nodes_outdoor = gdf_refug[gdf_refug["tipo"] == "outdoor"]["nearest_node"].unique().tolist()
    nodes_indoor = gdf_refug[gdf_refug["tipo"] == "indoor"]["nearest_node"].unique().tolist()

    print(f"  -> Nodos fuente OUTDOOR: {len(nodes_outdoor)}")
    print(f"  -> Nodos fuente INDOOR : {len(nodes_indoor)}")

    # Descargar edificios
    print("\n  Descargando edificios residenciales de Bilbao...")
    try:
        gdf_buildings = ox.features_from_place(place_name, tags=building_tags)
    except Exception as e:
        print("\n*** ERROR al descargar edificios ***")
        print(e)
        return

    gdf_buildings = gdf_buildings[~gdf_buildings.geometry.isna()].copy()
    if gdf_buildings.empty:
        print("No se han obtenido edificios con esos tags. Fin.")
        return

    total_buildings = len(gdf_buildings)
    print(f"  -> Total edificios seleccionados: {total_buildings}")

    # Centroide de cada edificio
    # reproyectar para centroid correcto
    gdf_buildings_proj = gdf_buildings.to_crs(25830)
    gdf_buildings["centroid"] = gdf_buildings_proj.geometry.centroid

    # convertir centroides a lat/lon
    gdf_buildings["centroid"] = gdf_buildings["centroid"].to_crs(4326)
    bx = gdf_buildings["centroid"].x.values
    by = gdf_buildings["centroid"].y.values


    # Nodos más cercanos a cada edificio
    building_nodes = ox.distance.nearest_nodes(G_walk, X=list(bx), Y=list(by))
    gdf_buildings["nearest_node"] = list(building_nodes)

    # --------------------------------------------------------------
    # 4. Dijkstra multi-fuente a cutoff_m m por la red
    # --------------------------------------------------------------
    print("\nPaso 4/5: calculando distancias mínimas por la red (Dijkstra)...")

    # OUTDOOR
    if nodes_outdoor:
        print(f"  -> Dijkstra multi-fuente OUTDOOR (cutoff = {cutoff_m} m)...")
        dist_outdoor = nx.multi_source_dijkstra_path_length(
            G_walk,
            sources=nodes_outdoor,
            cutoff=cutoff_m,
            weight="length",
        )
    else:
        print("  -> No hay refugios OUTDOOR.")
        dist_outdoor = {}

    # INDOOR
    if nodes_indoor:
        print(f"  -> Dijkstra multi-fuente INDOOR (cutoff = {cutoff_m} m)...")
        dist_indoor = nx.multi_source_dijkstra_path_length(
            G_walk,
            sources=nodes_indoor,
            cutoff=cutoff_m,
            weight="length",
        )
    else:
        print("  -> No hay refugios INDOOR.")
        dist_indoor = {}

    # COMBINADO (OUT ∪ IN)
    nodes_all = nodes_outdoor + nodes_indoor
    if nodes_all:
        print(f"  -> Dijkstra multi-fuente COMBINADO (cutoff = {cutoff_m} m)...")
        dist_combined = nx.multi_source_dijkstra_path_length(
            G_walk,
            sources=nodes_all,
            cutoff=cutoff_m,
            weight="length",
        )
    else:
        print("  -> No hay refugios en absoluto (ni outdoor ni indoor). Fin.")
        return

    # --------------------------------------------------------------
    # 5. Clasificar edificios según cobertura en red
    # --------------------------------------------------------------
    print("\nPaso 5/5: clasificando edificios según cobertura en red...")

    # Para cada edificio miramos si su nodo está en los diccionarios dist_*
    node_series = gdf_buildings["nearest_node"]

    mask_outdoor = node_series.map(lambda n: n in dist_outdoor)
    mask_indoor = node_series.map(lambda n: n in dist_indoor)
    mask_combined = node_series.map(lambda n: n in dist_combined)

    n_outdoor = int(mask_outdoor.sum())
    n_indoor = int(mask_indoor.sum())
    n_combined = int(mask_combined.sum())

    pct_outdoor = (n_outdoor / total_buildings) * 100 if total_buildings > 0 else 0
    pct_indoor = (n_indoor / total_buildings) * 100 if total_buildings > 0 else 0
    pct_combined = (n_combined / total_buildings) * 100 if total_buildings > 0 else 0

    print(f"\n================= RESULTADOS ({cutoff_m} m por red) =================")
    print(f"Total edificios (building-tags seleccionados): {total_buildings}")
    print("")
    print(f"Edificios con distancia en red ≤ {cutoff_m} m a algún refugio OUTDOOR: "
          f"{n_outdoor} ({pct_outdoor:.2f} % del total)")
    print(f"Edificios con distancia en red ≤ {cutoff_m} m a algún refugio INDOOR : "
          f"{n_indoor} ({pct_indoor:.2f} % del total)")
    print(f"Edificios con distancia en red ≤ {cutoff_m} m a algún refugio (OUT ∪ IN): "
          f"{n_combined} ({pct_combined:.2f} % del total)")
    print("==============================================================\n")

    # Si quieres guardar los edificios etiquetados para GIS:
    # gdf_buildings["in_outdoor_net"] = mask_outdoor
    # gdf_buildings["in_indoor_net"] = mask_indoor
    # gdf_buildings["in_combined_net"] = mask_combined
    # gdf_buildings.to_file("edificios_cobertura_red.gpkg", layer="edificios", driver="GPKG")


if __name__ == "__main__":
    main()