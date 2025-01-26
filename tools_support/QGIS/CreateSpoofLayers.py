def CreateSpoofLayers(layer_name="spoof", run_dir=None, output_shapefile=None, highlight_clusters=None):
    """
    Creates QGIS layers with 3 points, lines, and polygons representing drift areas.
    The polygon's color matches the cluster's point layers.

    Parameters:
    - layer_name: Name of the QGIS layers.
    - run_dir: Directory containing the CSV files.
    - output_shapefile: Path to save the layers as shapefiles (optional).
    - highlight_clusters: List of cluster names to highlight (optional). If not None, only the specified clusters will be enabled, and the rest disabled.
    """

    # File paths
    spoof_cases_df_csv_file = f"{run_dir}/spoof_cases_df/spoof_cases_df.csv"
    spoof_clusters_gdf_csv_file = f"{run_dir}/spoof_clusters_gdf/spoof_clusters_gdf.csv"

    # Remove existing layers with the same names
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() in [
            layer_name + '_spoof_start_end_points',
            layer_name + '_spoof_target',
            layer_name + '_lines',
            layer_name + '_drift_area'
        ]:
            QgsProject.instance().removeMapLayer(layer.id())

    # Create memory layers
    point_layer_1_3 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_start_end_points', 'memory')
    provider_1_3 = point_layer_1_3.dataProvider()

    point_layer_2 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_target', 'memory')
    provider_2 = point_layer_2.dataProvider()

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
    provider_1_3.addAttributes(fields)
    provider_2.addAttributes(fields)
    line_provider.addAttributes([QgsField('cluster_num', QVariant.String)])
    drift_area_provider.addAttributes([QgsField('cluster_num', QVariant.String), QgsField('type', QVariant.String)])
    point_layer_1_3.updateFields()
    point_layer_2.updateFields()
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
                if cluster_num not in cluster_num_set:
                    cluster_nums.append(cluster_num)
                    cluster_num_set.add(cluster_num)
                    cluster_colors[cluster_num] = QColor(to_hex(colormap(len(cluster_colors) % colormap.N)))

                entry_lat, entry_lon = float(row['entry_lat']), float(row['entry_lon'])
                drift_lat, drift_lon = float(row['drift_lat']), float(row['drift_lon'])
                exit_lat, exit_lon = float(row['exit_lat']), float(row['exit_lon'])

                if not (entry_lat and entry_lon and drift_lat and drift_lon and exit_lat and exit_lon):
                    continue

                point1 = QgsFeature()
                point1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(entry_lon, entry_lat)))
                point1.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_1_3.addFeature(point1)

                point3 = QgsFeature()
                point3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(exit_lon, exit_lat)))
                point3.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_1_3.addFeature(point3)

                point2 = QgsFeature()
                point2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(drift_lon, drift_lat)))
                point2.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_2.addFeature(point2)

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
                last_row = rows[-1]
                drift_area = last_row.get('drift_area')
                cluster_num = last_row.get('cluster_num')
                type_value = last_row.get('type')

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

    except FileNotFoundError:
        print(f"File not found: {spoof_clusters_gdf_csv_file}")

    # Add layers to the project
    QgsProject.instance().addMapLayer(point_layer_1_3)
    QgsProject.instance().addMapLayer(point_layer_2)
    QgsProject.instance().addMapLayer(line_layer)
    QgsProject.instance().addMapLayer(drift_area_layer)

    # Apply categorized styling
    categories_1_3 = []
    categories_2 = []
    line_categories = []
    polygon_categories = []

    for cluster_num, color in cluster_colors.items():
        symbol_1_3 = QgsMarkerSymbol.defaultSymbol(point_layer_1_3.geometryType())
        symbol_2 = QgsMarkerSymbol.defaultSymbol(point_layer_2.geometryType())
        line_symbol = QgsLineSymbol.defaultSymbol(line_layer.geometryType())
        polygon_symbol = QgsMarkerSymbol.defaultSymbol(drift_area_layer.geometryType())

        symbol_1_3.symbolLayer(0).setColor(color)
        symbol_2.symbolLayer(0).setColor(color)
        symbol_2.setSize(10)
        line_symbol.symbolLayer(0).setColor(color)
        polygon_symbol.symbolLayer(0).setColor(color)

        categories_1_3.append(QgsRendererCategory(cluster_num, symbol_1_3, cluster_num))
        categories_2.append(QgsRendererCategory(cluster_num, symbol_2, cluster_num))
        line_categories.append(QgsRendererCategory(cluster_num, line_symbol, cluster_num))
        polygon_categories.append(QgsRendererCategory(cluster_num, polygon_symbol, cluster_num))

    point_layer_1_3.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_1_3))
    point_layer_2.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', categories_2))
    line_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', line_categories))
    drift_area_layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_num', polygon_categories))
