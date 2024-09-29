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

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsMarkerSymbol,
    QgsLineSymbol, QgsVectorFileWriter
)
from PyQt5.QtCore import QVariant
from matplotlib import cm  # Import colormap functionality from matplotlib
from matplotlib.colors import to_hex  # Convert RGB to hex
from PyQt5.QtGui import QColor  # Import QColor for handling colors

def create_spoof_layer_mod(events_df, layer_name, output_shapefile=None):
    """
    Creates QGIS layers with 3 points from an events DataFrame and draws lines between them.
    The second point is placed in a separate layer and is twice as large.
    Lines are drawn between the first and second points, and between the second and third points.
    
    Both point layers and the line layer are categorized by 'cluster', with point 2 being larger.
    
    Parameters:
    - events_df: DataFrame containing event information with columns:
        ['start_latitude_pre', 'start_longitude_pre', 'start_latitude', 'start_longitude', 
         'end_latitude', 'end_longitude', 'start_time', 'end_time', 'cluster_num']
    - layer_name: Name of the QGIS layers.
    - output_shapefile: Path to save the layers as shapefiles (optional).
    """

    # Remove existing layers with the same names
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() in [layer_name + '_spoof_start_end_points', layer_name + '_spoof_target', layer_name + '_lines']:
            QgsProject.instance().removeMapLayer(layer.id())

    # Create memory layers for points and lines
    point_layer_1_3 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_start_end_points', 'memory')
    provider_1_3 = point_layer_1_3.dataProvider()

    point_layer_2 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_target', 'memory')
    provider_2 = point_layer_2.dataProvider()

    line_layer = QgsVectorLayer('LineString?crs=EPSG:4326', layer_name + '_lines', 'memory')
    line_provider = line_layer.dataProvider()

    # Define fields for the point and line layers
    fields = [
        QgsField('cluster', QVariant.String),
        QgsField('start_time', QVariant.String),
        QgsField('end_time', QVariant.String),
        QgsField('type', QVariant.String),
    ]
    provider_1_3.addAttributes(fields)
    provider_2.addAttributes(fields)
    line_provider.addAttributes([QgsField('cluster', QVariant.String)])
    point_layer_1_3.updateFields()
    point_layer_2.updateFields()
    line_layer.updateFields()

    cluster_nums = []
    cluster_num_set = set()  # To keep track of unique cluster numbers

    # Iterate through the events DataFrame and add points and lines to the layers
    for index, row in events_df.iterrows():
        try:
            # Collect unique cluster numbers in the original order
            cluster_num = row['cluster_num']
            if cluster_num not in cluster_num_set:
                cluster_nums.append(cluster_num)
                cluster_num_set.add(cluster_num)

            # Point 1: start_latitude_pre, start_longitude_pre
            start_latitude_pre = float(row['start_latitude_pre']) if row['start_latitude_pre'] else None
            start_longitude_pre = float(row['start_longitude_pre']) if row['start_longitude_pre'] else None
            
            # Point 2: start_latitude, start_longitude (this will be in a separate layer)
            start_latitude = float(row['start_latitude']) if row['start_latitude'] else None
            start_longitude = float(row['start_longitude']) if row['start_longitude'] else None
            
            # Point 3: end_latitude, end_longitude
            end_latitude = float(row['end_latitude']) if row['end_latitude'] else None
            end_longitude = float(row['end_longitude']) if row['end_longitude'] else None
            
            if not (start_latitude_pre and start_longitude_pre and start_latitude and start_longitude and end_latitude and end_longitude):
                continue  # Skip rows with missing or invalid data
            
            # Create features for points 1 and 3
            point1 = QgsFeature()
            point1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(start_longitude_pre, start_latitude_pre)))
            point1.setAttributes([cluster_num, row['start_time'].strftime("%Y-%m-%d %H:%M:%S"), row['end_time'].strftime("%Y-%m-%d %H:%M:%S"), row['type']])
            provider_1_3.addFeature(point1)

            point3 = QgsFeature()
            point3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(end_longitude, end_latitude)))
            point3.setAttributes([cluster_num, row['start_time'].strftime("%Y-%m-%d %H:%M:%S"), row['end_time'].strftime("%Y-%m-%d %H:%M:%S"), row['type']])
            provider_1_3.addFeature(point3)

            # Create a feature for point 2
            point2 = QgsFeature()
            point2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(start_longitude, start_latitude)))
            point2.setAttributes([cluster_num, row['start_time'].strftime("%Y-%m-%d %H:%M:%S"), row['end_time'].strftime("%Y-%m-%d %H:%M:%S"), row['type']])
            provider_2.addFeature(point2)

            # Create a line between Point 1 and Point 2
            line1 = QgsFeature()
            line1.setGeometry(QgsGeometry.fromPolylineXY([
                QgsPointXY(start_longitude_pre, start_latitude_pre),
                QgsPointXY(start_longitude, start_latitude)
            ]))
            line1.setAttributes([cluster_num])
            line_provider.addFeature(line1)

            # Create a line between Point 3 and Point 2
            line2 = QgsFeature()
            line2.setGeometry(QgsGeometry.fromPolylineXY([
                QgsPointXY(end_longitude, end_latitude),
                QgsPointXY(start_longitude, start_latitude)
            ]))
            line2.setAttributes([cluster_num])
            line_provider.addFeature(line2)

        except ValueError as e:
            print(f"Error processing row {index}: {e}")
            continue

    # Add the point and line layers to the QGIS project
    QgsProject.instance().addMapLayer(point_layer_1_3)
    QgsProject.instance().addMapLayer(point_layer_2)
    QgsProject.instance().addMapLayer(line_layer)

    # Create a color map that will be used for points and lines
    categories_1_3 = []
    categories_2 = []
    line_categories = []
    
    # Create a colormap from matplotlib
    colormap = cm.get_cmap('tab20', len(cluster_nums))  # Using 'tab20' for distinct colors

    for i, cluster_num in enumerate(cluster_nums):
        # Create symbols for points 1 and 3
        symbol_1_3 = QgsMarkerSymbol.defaultSymbol(point_layer_1_3.geometryType())
        symbol_2 = QgsMarkerSymbol.defaultSymbol(point_layer_2.geometryType())
        line_symbol = QgsLineSymbol.defaultSymbol(line_layer.geometryType())

        color = QColor(to_hex(colormap(i)))  # Convert hex to QColor

        # Set colors for symbols
        symbol_1_3.symbolLayer(0).setColor(color)
        symbol_2.symbolLayer(0).setColor(color)
        symbol_2.setSize(10)  # Set larger size for point 2
        line_symbol.symbolLayer(0).setColor(color)

        # Create categories for both layers
        category_1_3 = QgsRendererCategory(str(cluster_num), symbol_1_3, str(cluster_num))  # Ensure it's a string
        category_2 = QgsRendererCategory(str(cluster_num), symbol_2, str(cluster_num))  # Ensure it's a string
        line_category = QgsRendererCategory(str(cluster_num), line_symbol, str(cluster_num))  # Ensure it's a string

        categories_1_3.append(category_1_3)
        categories_2.append(category_2)
        line_categories.append(line_category)

    # Apply the categorized renderers to the point and line layers
    categorized_renderer_1_3 = QgsCategorizedSymbolRenderer('cluster', categories_1_3)
    point_layer_1_3.setRenderer(categorized_renderer_1_3)

    categorized_renderer_2 = QgsCategorizedSymbolRenderer('cluster', categories_2)
    point_layer_2.setRenderer(categorized_renderer_2)

    line_categorized_renderer = QgsCategorizedSymbolRenderer('cluster', line_categories)
    line_layer.setRenderer(line_categorized_renderer)

    # Optionally save the layers as shapefiles
    if output_shapefile:
        point_output_1_3 = output_shapefile + '_spoof_start_end_points.shp'
        point_output_2 = output_shapefile + '_spoof_target.shp'
        line_output = output_shapefile + '_lines.shp'

        QgsVectorFileWriter.writeAsVectorFormat(point_layer_1_3, point_output_1_3, "UTF-8", point_layer_1_3.crs(), "ESRI Shapefile")
        QgsVectorFileWriter.writeAsVectorFormat(point_layer_2, point_output_2, "UTF-8", point_layer_2.crs(), "ESRI Shapefile")
        QgsVectorFileWriter.writeAsVectorFormat(line_layer, line_output, "UTF-8", line_layer.crs(), "ESRI Shapefile")

        print(f'Successfully saved point layers to {point_output_1_3} and {point_output_2}')
        print(f'Successfully saved line layer to {line_output}')
    else:
        print('Layers added to QGIS project but not saved to disk.')
