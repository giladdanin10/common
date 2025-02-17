
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
def CreateSpoofLayers(layer_name="spoof",
                      spoof_cases_df_file=None,
                      spoof_clusters_gdf_file = None,
                    output_shapefile=None,
                      highlight_clusters=None,
                        iteration_num=None, 
                        exclude_clusters=None,
                        file_name_prefix="",
                        max_num_clusters = 100,
                        layer_types = ['entry_points','exit_points','drift_point','lines','drift_area']):
    """
    Creates QGIS layers with separate entry and exit points, lines, and polygons representing drift areas.
    The polygon's color matches the cluster's point layers, and entry points are slightly larger than exit points.

    Parameters:
    - layer_name: Name of the QGIS layers.
    - run_dir: Directory containing the CSV files.
    - output_shapefile: Path to save the layers as shapefiles (optional).
    - highlight_clusters: List of cluster names to include (optional). Only these clusters will be added if provided.
    - iteration_num: Specific iteration number to filter drift areas. If None, the last iteration is used.
    - exclude_clusters: List of cluster names to exclude (optional). These clusters will be skipped.
    """

    # File paths

    # add_spoof_cases_layers = spoof_cases_df_file is not None
    # add_drift_area_layer = spoof_clusters_gdf_file is not None


    # Remove existing layers with the same names
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() in [
            layer_name + '_entry_points',
            layer_name + '_exit_points',
            layer_name + '_drift_point',
            layer_name + '_lines',
            layer_name + '_drift_area'
        ]:
            QgsProject.instance().removeMapLayer(layer.id())

    # Create memory layers
    if ('entry_points' in layer_types):
        entry_points_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_entry_points', 'memory')
        provider_entry = entry_points_layer.dataProvider()
    
    if ('exit_points' in layer_types):
        exit_points_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_exit_points', 'memory')
        provider_exit = exit_points_layer.dataProvider()

    if ('drift_points') in layer_types:
        drift_point_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_drift_point', 'memory')
        provider_drift = drift_point_layer.dataProvider()

    if ('entry_exit_drift_lines') in layer_types:
        line_layer = QgsVectorLayer('LineString?crs=EPSG:4326', layer_name + '_lines', 'memory')
        line_provider = line_layer.dataProvider()

    if ('drift_areas') in layer_types:
        drift_area_layer = QgsVectorLayer('Polygon?crs=EPSG:4326', layer_name + '_drift_area', 'memory')
        drift_area_provider = drift_area_layer.dataProvider()

    # Define fields
    fields = [
        QgsField('cluster_num', QVariant.String),
        QgsField('start_time', QVariant.String),
        QgsField('end_time', QVariant.String),
        QgsField('type', QVariant.String),
        QgsField('vessel_id', QVariant.String)
    ]

    if ('entry_points' in layer_types):
        provider_entry.addAttributes(fields)

    if ('exit_points' in layer_types):
        provider_exit.addAttributes(fields)

    if ('drift_points') in layer_types:
        provider_drift.addAttributes(fields)

    if ('entry_exit_drift_lines') in layer_types:
        line_provider.addAttributes([QgsField('cluster_num', QVariant.String)])


    if ('drift_areas') in layer_types:
        drift_area_provider.addAttributes([QgsField('cluster_num', QVariant.String), QgsField('type', QVariant.String)])

    if ('entry_points' in layer_types):
        entry_points_layer.updateFields()

    if ('exit_points' in layer_types):
        exit_points_layer.updateFields()

    if ('drift_points') in layer_types:
        drift_point_layer.updateFields()

    if ('entry_exit_drift_lines') in layer_types:        
        line_layer.updateFields()

    if ('drift_areas') in layer_types:
        drift_area_layer.updateFields()

    cluster_nums = []
    cluster_num_set = set()
    colormap = cm.get_cmap('tab20', 20)
    cluster_colors = {}

    # Generate a fixed colormap
    fixed_colormap = cm.get_cmap('gist_ncar', max_num_clusters)

    # sequential_colors_list = [mcolors.to_hex(fixed_colormap(i / max_num_clusters)) for i in range(max_num_clusters)]
    sequential_colors_list = [QColor(mcolors.to_hex(fixed_colormap(i / max_num_clusters))) for i in range(max_num_clusters)]

    # Shuffle the color order randomly    
    color_index = np.random.permutation(max_num_clusters)
    colors_list = [sequential_colors_list[i] for i in color_index]




    # Process points and lines
    if (spoof_cases_df_file is not None):
        # with open(spoof_cases_df_file, newline='', encoding='utf-8') as f:
        #     reader = csv.DictReader(f)
        #     reader
        #     for row in reader:

        spoof_cases_df = pd.read_csv(spoof_cases_df_file)
        spoof_cases_df.sort_values(by=['cluster_num'], inplace=True)

# filter by exclude_clusters
        if exclude_clusters is not None:
            spoof_cases_df = spoof_cases_df[~spoof_cases_df['cluster_num'].isin(exclude_clusters)]

        if highlight_clusters is not None:
            spoof_cases_df = spoof_cases_df[spoof_cases_df['cluster_num'].isin(highlight_clusters)]

        

        cluster_ind = 0
        if (highlight_clusters) is not None:    
            highlight_clusters_str = [str(i) for i in highlight_clusters]
        else:
            highlight_clusters_str = None
            
        for ind, row in spoof_cases_df.iterrows():
                try:
                    cluster_num = str(row['cluster_num'])
                    # if (cluster_num==3):
                    #     print("cluster_num:",cluster_num)

                    # Filter clusters based on include/exclude logic
                    # if exclude_clusters and cluster_num in exclude_clusters:
                    #     continue
                    if highlight_clusters_str is not None and cluster_num not in highlight_clusters_str:
                        continue
                    
                    if cluster_num not in cluster_num_set:
                        cluster_ind = cluster_ind+1
                        # print(cluster_ind)
                        cluster_nums.append(cluster_num)
                        cluster_num_set.add(cluster_num)
                        temp = QColor(to_hex(colormap(len(cluster_colors) % colormap.N)))
                        cluster_colors[cluster_num] = colors_list[cluster_ind]                    
                        
                    # entry_lat = None
                    # entry_lon = None
                    # drift_lat = None
                    # drift_lon = None
                    # exit_lat = None
                    # exit_lon = None

                    if ('entry_points' in layer_types):
                        entry_lat, entry_lon = float(row['entry_lat']), float(row['entry_lon'])

                    if ('drift_points') in layer_types:
                        drift_lat, drift_lon = float(row['drift_lat']), float(row['drift_lon'])

                    if ('exit_points' in layer_types):    
                        exit_lat, exit_lon = float(row['exit_lat']), float(row['exit_lon'])

                    # if not (entry_lat and entry_lon and drift_lat and drift_lon and exit_lat and exit_lon):
                    #     continue

                    # Entry Point
                    if ('entry_points' in layer_types):
                        entry_feature = QgsFeature()
                        entry_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(entry_lon, entry_lat)))
                        entry_feature.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                        provider_entry.addFeature(entry_feature)

                    # Exit Point
                    if ('exit_points' in layer_types):
                        exit_feature = QgsFeature()
                        exit_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(exit_lon, exit_lat)))
                        exit_feature.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                        provider_exit.addFeature(exit_feature)

                    # drift Point
                    if ('drift_points') in layer_types:
                        drift_feature = QgsFeature()
                        drift_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(drift_lon, drift_lat)))
                        drift_feature.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                        provider_drift.addFeature(drift_feature)

                    # Lines
                    if ('entry_exit_drift_lines') in layer_types:
                        line1 = QgsFeature()
                        line1.setGeometry(QgsGeometry.fromPolylineXY([
                            QgsPointXY(entry_lon, entry_lat),
                            QgsPointXY(drift_lon, drift_lat)
                        ]))
                        line1.setAttributes([cluster_num])
                        line_provider.addFeature(line1)

                        line2 = QgsFeature()
                        line2.setGeometry(QgsGeometry.fromPolylineXY([
                            QgsPointXY(exit_lon, exit_lat),
                            QgsPointXY(drift_lon, drift_lat)
                        ]))
                        line2.setAttributes([cluster_num])
                        line_provider.addFeature(line2)

                except ValueError:
                    continue
    
        if ('drift_areas') in layer_types:
        # Process polygons for drift_area
            spoof_clusters_gdf_org = pd.read_csv(spoof_clusters_gdf_file)

# filter by iteration_num
            if iteration_num is None:
                iteration_num = spoof_clusters_gdf_org['iteration_num'].max()

            spoof_clusters_gdf = spoof_clusters_gdf_org[spoof_clusters_gdf_org['iteration_num'] == iteration_num]

# filter by exclude_clusters
            if exclude_clusters is not None:
                spoof_clusters_gdf = spoof_clusters_gdf[~spoof_clusters_gdf['cluster_num'].isin(exclude_clusters)]

            if highlight_clusters is not None:
                spoof_clusters_gdf = spoof_clusters_gdf[spoof_clusters_gdf['cluster_num'].isin(highlight_clusters)]

            for ind, row in spoof_clusters_gdf.iterrows():
                cluster_num = row['cluster_num']

                # Filter clusters based on include/exclude logic
                # if exclude_clusters and cluster_num in exclude_clusters:
                #     continue
                # if highlight_clusters and cluster_num not in highlight_clusters:
                #     continue

                drift_area = row['drift_area']

                try:
                    if drift_area:
                        points = [
                            QgsPointXY(float(coord.split()[0]), float(coord.split()[1]))
                            for coord in drift_area.replace('MULTIPOINT (', '').replace(')', '').split(',')
                        ]

                        if len(points) > 2:
                            polygon = QgsGeometry.fromPolygonXY([points])
                            drift_feature = QgsFeature()
                            drift_feature.setGeometry(polygon)
                            drift_feature.setAttributes([cluster_num])
                            drift_area_provider.addFeature(drift_feature)
                except ValueError:
                    continue

        # try:            
        #     with open(spoof_clusters_gdf_file, newline='', encoding='utf-8') as f:
        #         reader = csv.DictReader(f)
        #         rows = list(reader)
        #         if rows:
        #             # Determine the iteration_num
        #             if iteration_num is None:
        #                 iteration_num = max(int(row['iteration_num']) for row in rows if row['iteration_num'].isdigit())

        #             filtered_rows = [row for row in rows if int(row['iteration_num']) == iteration_num]
        #             for row in filtered_rows:
        #                 cluster_num = row.get('cluster_num')

        #                 # Filter clusters based on include/exclude logic
        #                 # if exclude_clusters and cluster_num in exclude_clusters:
        #                 #     continue
        #                 # if highlight_clusters and cluster_num not in highlight_clusters:
        #                 #     continue

        #                 drift_area = row.get('drift_area')
        #                 type_value = row.get('type')

        #                 try:
        #                     if drift_area:
        #                         points = [
        #                             QgsPointXY(float(coord.split()[0]), float(coord.split()[1]))
        #                             for coord in drift_area.replace('MULTIPOINT (', '').replace(')', '').split(',')
        #                         ]

        #                         if len(points) > 2:
        #                             polygon = QgsGeometry.fromPolygonXY([points])
        #                             drift_feature = QgsFeature()
        #                             drift_feature.setGeometry(polygon)
        #                             drift_feature.setAttributes([cluster_num, type_value])
        #                             drift_area_provider.addFeature(drift_feature)
        #                 except ValueError:
        #                     continue

        # except FileNotFoundError:
        #     print(f"File not found: {spoof_clusters_gdf_file}")

    # Add layers to the project
    if ('entry_points' in layer_types):
        QgsProject.instance().addMapLayer(entry_points_layer)

    if ('exit_points' in layer_types):
        QgsProject.instance().addMapLayer(exit_points_layer)

    if ('drift_points') in layer_types:
        QgsProject.instance().addMapLayer(drift_point_layer)

    if ('entry_exit_drift_lines') in layer_types:
        QgsProject.instance().addMapLayer(line_layer)

    if ('drift_areas') in layer_types:
        QgsProject.instance().addMapLayer(drift_area_layer)

    # Apply categorized styling
    categories_entry = []
    categories_exit = []
    categories_drift = []
    line_categories = []
    polygon_categories = []

    for cluster_num, color in cluster_colors.items():
        # Entry Points
        if ('entry_points' in layer_types):
            symbol_entry = QgsMarkerSymbol.defaultSymbol(entry_points_layer.geometryType())
            symbol_entry.symbolLayer(0).setColor(color)
            symbol_entry.setSize(4)  # Larger size for entry points

        # Exit Points
        if ('exit_points' in layer_types):
            symbol_exit = QgsMarkerSymbol.defaultSymbol(exit_points_layer.geometryType())
            symbol_exit.symbolLayer(0).setColor(color)
            symbol_exit.setSize(3)  # Smaller size for exit points

        # drift Points
        if ('drift_points') in layer_types:
            symbol_drift = QgsMarkerSymbol.defaultSymbol(drift_point_layer.geometryType())
            symbol_drift.symbolLayer(0).setColor(color)
            symbol_drift.setSize(10)

        # Lines
        if ('entry_exit_drift_lines') in layer_types:
            line_symbol = QgsLineSymbol.defaultSymbol(line_layer.geometryType())
            line_symbol.symbolLayer(0).setColor(color)

        # Polygons
        if ('drift_areas') in layer_types:
            polygon_symbol = QgsFillSymbol.defaultSymbol(drift_area_layer.geometryType())
            polygon_symbol.setColor(color)
            polygon_symbol.setOpacity(0.4)  # Set opacity to 40%

        if ('entry_points' in layer_types):
            categories_entry.append(QgsRendererCategory(cluster_num, symbol_entry, cluster_num))

        if ('exit_points' in layer_types):             
            categories_exit.append(QgsRendererCategory(cluster_num, symbol_exit, cluster_num))

        if ('drift_points') in layer_types:
            categories_drift.append(QgsRendererCategory(cluster_num, symbol_drift, cluster_num))

        if ('entry_exit_drift_lines') in layer_types:
            line_categories.append(QgsRendererCategory(cluster_num, line_symbol, cluster_num))

        if ('drift_areas') in layer_types:
            polygon_categories.append(QgsRendererCategory(cluster_num, polygon_symbol, cluster_num))

    if ('entry_points' in layer_types):
        entry_points_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_entry))
        
    if ('exit_points' in layer_types):
        exit_points_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_exit))

    if ('drift_points') in layer_types:
        drift_point_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_drift))
        
    if ('entry_exit_drift_lines') in layer_types:
        line_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', line_categories))

    if ('drift_areas') in layer_types:
        drift_area_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', polygon_categories))
