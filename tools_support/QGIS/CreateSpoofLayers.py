import csv
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsMarkerSymbol,
    QgsLineSymbol, QgsVectorFileWriter
)
from PyQt5.QtCore import QVariant
from matplotlib import cm  # Import colormap functionality from matplotlib
from matplotlib.colors import to_hex  # Convert RGB to hex
from PyQt5.QtGui import QColor  # Import QColor for handling colors


def CreateSpoofLayers(layer_name, csv_file, output_shapefile=None, highlight_clusters=None):
    """
    Creates QGIS layers with 3 points from a CSV file and draws lines between them.
    The second point is placed in a separate layer and is twice as large.
    Lines are drawn between the first and second points, and between the second and third points.
    
    Both point layers and the line layer are categorized by 'cluster_num', with point 2 being larger,
    and the classification names (ship names) are maintained in the order they appear in the CSV file.
    
    Parameters:
    - csv_file: Path to the CSV file.
    - layer_name: Name of the QGIS layers.
    - output_shapefile: Path to save the layers as shapefiles (optional).
    - highlight_clusters: List of cluster names to highlight (optional). If not None, only the specified clusters will be enabled, and the rest disabled.
    """

    # Remove existing layers with the same names
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() == layer_name + '_spoof_start_end_points' or layer.name() == layer_name + '_spoof_target' or layer.name() == layer_name + '_lines':
            QgsProject.instance().removeMapLayer(layer.id())

    # Create a memory layer to hold points 1 and 3
    point_layer_1_3 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_start_end_points', 'memory')
    provider_1_3 = point_layer_1_3.dataProvider()

    # Create a memory layer to hold point 2
    point_layer_2 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_target', 'memory')
    provider_2 = point_layer_2.dataProvider()

    # Create a memory layer to hold lines
    line_layer = QgsVectorLayer('LineString?crs=EPSG:4326', layer_name + '_lines', 'memory')
    line_provider = line_layer.dataProvider()

    # Define fields for the point and line layers
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
    point_layer_1_3.updateFields()
    point_layer_2.updateFields()
    line_layer.updateFields()

    cluster_nums = []
    cluster_num_set = set()  # To keep track of unique ship names in the original order

    # Read the CSV and add the points and lines to the layers
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Collect unique ship names in the original order
                cluster_num = row['cluster_num']
                if cluster_num not in cluster_num_set:
                    cluster_nums.append(cluster_num)
                    cluster_num_set.add(cluster_num)

                # Point 1: entry_lat_pre, entry_lon_pre
                entry_lat = float(row['entry_lat']) if row['entry_lat'] else None
                entry_lon = float(row['entry_lon']) if row['entry_lon'] else None

                
                # Point 2: entry_lat, entry_lon (this will be in a separate layer)
                drift_lat = float(row['drift_lat']) if row['drift_lat'] else None
                drift_lon = float(row['drift_lon']) if row['drift_lon'] else None
                
                # Point 3: exit_lat, exit_lon
                exit_lat = float(row['exit_lat']) if row['exit_lat'] else None
                exit_lon = float(row['exit_lon']) if row['exit_lon'] else None
                

                if not (entry_lat and entry_lon and drift_lat and drift_lon and exit_lat and exit_lon):
                    continue  # Skip rows with missing or invalid data
                
                # Create features for points 1 and 3
                point1 = QgsFeature()
                point1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(entry_lon, entry_lat)))

                point1.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_1_3.addFeature(point1)

                point3 = QgsFeature()
                point3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(exit_lon, exit_lat)))
                point3.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_1_3.addFeature(point3)

                # Create a feature for point 2
                point2 = QgsFeature()
                point2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(drift_lon, drift_lat)))

                point2.setAttributes([cluster_num, row['start_time'], row['end_time'], row['type'], row['vessel_id']])
                provider_2.addFeature(point2)

                # Create a line between Point 1 and Point 2
                line1 = QgsFeature()
                line1.setGeometry(QgsGeometry.fromPolylineXY([
                    QgsPointXY(entry_lon, entry_lat),
                    QgsPointXY(drift_lon, drift_lat)
                ]))
                
                line1.setAttributes([cluster_num])
                line_provider.addFeature(line1)

                # Create a line between Point 3 and Point 2
                line2 = QgsFeature()
                line2.setGeometry(QgsGeometry.fromPolylineXY([
                    QgsPointXY(exit_lon, exit_lat),
                    QgsPointXY(drift_lon, drift_lat)
                ]))


                line2.setAttributes([cluster_num])
                line_provider.addFeature(line2)

            except ValueError as e:
                print(f"Error processing row: {e}")
                continue

    # Add the point and line layers to the QGIS project
    QgsProject.instance().addMapLayer(point_layer_1_3)
    QgsProject.instance().addMapLayer(point_layer_2)
    QgsProject.instance().addMapLayer(line_layer)

    # Create a colormap from matplotlib
    if len(cluster_nums) <= 10:
        colormap = cm.get_cmap('Set1', len(cluster_nums))  # Use 'Set1' for highly distinguishable colors
    else:
        colormap = cm.get_cmap('tab20', len(cluster_nums))  # Use 'tab20' for a larger number of categories

    categories_1_3 = []
    categories_2 = []
    line_categories = []

    for i, cluster_num in enumerate(cluster_nums):
        # Create symbols for points 1 and 3
        symbol_1_3 = QgsMarkerSymbol.defaultSymbol(point_layer_1_3.geometryType())
        symbol_2 = QgsMarkerSymbol.defaultSymbol(point_layer_2.geometryType())
        line_symbol = QgsLineSymbol.defaultSymbol(line_layer.geometryType())

        color = QColor(to_hex(colormap(i)))  # Convert hex to QColor

        # Assign a consistent color for both point layers and lines based on ship name
        symbol_1_3.symbolLayer(0).setColor(color)
        symbol_2.symbolLayer(0).setColor(color)
        symbol_2.setSize(10)  # Set larger size for point 2
        line_symbol.symbolLayer(0).setColor(color)

        # print(type(cluster_num))
        # Enable only highlighted clusters if highlight_clusters is provided
        if highlight_clusters is None or int(cluster_num) in highlight_clusters:
            enabled = True
        else:
            enabled = False

        # Create categories for both layers
        category_1_3 = QgsRendererCategory(cluster_num, symbol_1_3, cluster_num, enabled)
        category_2 = QgsRendererCategory(cluster_num, symbol_2, cluster_num, enabled)
        line_category = QgsRendererCategory(cluster_num, line_symbol, cluster_num, enabled)

        categories_1_3.append(category_1_3)
        categories_2.append(category_2)
        line_categories.append(line_category)

    # Apply the categorized renderers to the point and line layers
    categorized_renderer_1_3 = QgsCategorizedSymbolRenderer('cluster_num', categories_1_3)
    point_layer_1_3.setRenderer(categorized_renderer_1_3)

    categorized_renderer_2 = QgsCategorizedSymbolRenderer('cluster_num', categories_2)
    point_layer_2.setRenderer(categorized_renderer_2)

    line_categorized_renderer = QgsCategorizedSymbolRenderer('cluster_num', line_categories)
    line_layer.setRenderer(line_categorized_renderer)

    # Optionally save the layers as shapefiles
