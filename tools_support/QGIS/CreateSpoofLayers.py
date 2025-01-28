def CreateSpoofLayers(layer_name="spoof", run_dir=None, output_shapefile=None, highlight_clusters=None, iteration_num=None, exclude_clusters=None,file_name_prefix=""):
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
    spoof_cases_df_csv_file = f"{run_dir}/spoof_cases_df/{file_name_prefix}spoof_cases_df.csv"
    spoof_clusters_gdf_csv_file = f"{run_dir}/spoof_clusters_gdf/{file_name_prefix}spoof_clusters_gdf.csv"

    # Remove existing layers with the same names
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() in [
            layer_name + '_entry_points',
            layer_name + '_exit_points',
            layer_name + '_drift_area',
            layer_name + '_lines',
            layer_name + '_drift_area'
        ]:
            QgsProject.instance().removeMapLayer(layer.id())

    # Create memory layers
    entry_points_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_entry_points', 'memory')
    provider_entry = entry_points_layer.dataProvider()

    exit_points_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_exit_points', 'memory')
    provider_exit = exit_points_layer.dataProvider()

    target_points_layer = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_drift_area', 'memory')
    provider_target = target_points_layer.dataProvider()

    line_layer = QgsVectorLayer('LineString?crs=EPSG:4326', layer_name + '_lines', 'memory')
    line_provider = line_layer.dataProvider()

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
    provider_entry.addAttributes(fields)
    provider_exit.addAttributes(fields)
    provider_target.addAttributes(fields)
    line_provider.addAttributes([QgsField('cluster_num', QVariant.String)])
    drift_area_provider.addAttributes([QgsField('cluster_num', QVariant.String), QgsField('type', QVariant.String)])
    entry_points_layer.updateFields()
    exit_points_layer.updateFields()
    target_points_layer.updateFields()
    line_layer.updateFields()
    drift_area_layer.updateFields()

    cluster_nums = []
    cluster_num_set = set()
    colormap = cm.get_cmap('tab20', 20)
    cluster_colors = {}

    # Process points and lines
    with open(spoof_cases_df_csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cluster_num = row['cluster_num']
                # if (cluster_num==3):
                #     print("cluster_num:",cluster_num)

                # Filter clusters based on include/exclude logic
                # if exclude_clusters and cluster_num in exclude_clusters:
                #     continue
                if highlight_clusters is not None and cluster_num not in highlight_clusters:
                    continue

                if cluster_num not in cluster_num_set:
                    cluster_nums.append(cluster_num)
                    cluster_num_set.add(cluster_num)
                    cluster_colors[cluster_num] = QColor(to_hex(colormap(len(cluster_colors) % colormap.N)))

                entry_lat, entry_lon = float(row['entry_lat']), float(row['entry_lon'])
                drift_lat, drift_lon = float(row['drift_lat']), float(row['drift_lon'])
                exit_lat, exit_lon = float(row['exit_lat']), float(row['exit_lon'])

                if not (entry_lat and entry_lon and drift_lat and drift_lon and exit_lat and exit_lon):
                    continue

                # Entry Point
                entry_feature = QgsFeature()
                entry_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(entry_lon, entry_lat)))
                entry_feature.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_entry.addFeature(entry_feature)

                # Exit Point
                exit_feature = QgsFeature()
                exit_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(exit_lon, exit_lat)))
                exit_feature.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_exit.addFeature(exit_feature)

                # Target Point
                target_feature = QgsFeature()
                target_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(drift_lon, drift_lat)))
                target_feature.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_target.addFeature(target_feature)

                # Lines
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

    # Process polygons for drift_area
    try:
        with open(spoof_clusters_gdf_csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                # Determine the iteration_num
                if iteration_num is None:
                    iteration_num = max(int(row['iteration_num']) for row in rows if row['iteration_num'].isdigit())

                filtered_rows = [row for row in rows if int(row['iteration_num']) == iteration_num]
                for row in filtered_rows:
                    cluster_num = row.get('cluster_num')

                    # Filter clusters based on include/exclude logic
                    # if exclude_clusters and cluster_num in exclude_clusters:
                    #     continue
                    # if highlight_clusters and cluster_num not in highlight_clusters:
                    #     continue

                    drift_area = row.get('drift_area')
                    type_value = row.get('type')

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
                                drift_feature.setAttributes([cluster_num, type_value])
                                drift_area_provider.addFeature(drift_feature)
                    except ValueError:
                        continue

    except FileNotFoundError:
        print(f"File not found: {spoof_clusters_gdf_csv_file}")

    # Add layers to the project
    QgsProject.instance().addMapLayer(entry_points_layer)
    QgsProject.instance().addMapLayer(exit_points_layer)
    QgsProject.instance().addMapLayer(target_points_layer)
    QgsProject.instance().addMapLayer(line_layer)
    QgsProject.instance().addMapLayer(drift_area_layer)

    # Apply categorized styling
    categories_entry = []
    categories_exit = []
    categories_target = []
    line_categories = []
    polygon_categories = []

    for cluster_num, color in cluster_colors.items():
        # Entry Points
        symbol_entry = QgsMarkerSymbol.defaultSymbol(entry_points_layer.geometryType())
        symbol_entry.symbolLayer(0).setColor(color)
        symbol_entry.setSize(4)  # Larger size for entry points

        # Exit Points
        symbol_exit = QgsMarkerSymbol.defaultSymbol(exit_points_layer.geometryType())
        symbol_exit.symbolLayer(0).setColor(color)
        symbol_exit.setSize(3)  # Smaller size for exit points

        # Target Points
        symbol_target = QgsMarkerSymbol.defaultSymbol(target_points_layer.geometryType())
        symbol_target.symbolLayer(0).setColor(color)
        symbol_target.setSize(10)

        # Lines
        line_symbol = QgsLineSymbol.defaultSymbol(line_layer.geometryType())
        line_symbol.symbolLayer(0).setColor(color)

        # Polygons
        polygon_symbol = QgsFillSymbol.defaultSymbol(drift_area_layer.geometryType())
        polygon_symbol.setColor(color)
        polygon_symbol.setOpacity(0.4)  # Set opacity to 40%

        categories_entry.append(QgsRendererCategory(cluster_num, symbol_entry, cluster_num))
        categories_exit.append(QgsRendererCategory(cluster_num, symbol_exit, cluster_num))
        categories_target.append(QgsRendererCategory(cluster_num, symbol_target, cluster_num))
        line_categories.append(QgsRendererCategory(cluster_num, line_symbol, cluster_num))
        polygon_categories.append(QgsRendererCategory(cluster_num, polygon_symbol, cluster_num))

    entry_points_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_entry))
    exit_points_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_exit))
    target_points_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_target))
    line_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', line_categories))
    drift_area_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', polygon_categories))
