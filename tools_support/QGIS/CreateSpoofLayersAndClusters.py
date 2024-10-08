import csv
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsMarkerSymbol,
    QgsLineSymbol, QgsVectorFileWriter,QgsFillSymbol,QgsSingleSymbolRenderer
)
from PyQt5.QtCore import QVariant
from matplotlib import cm  # Import colormap functionality from matplotlib
from matplotlib.colors import to_hex  # Convert RGB to hex
from PyQt5.QtGui import QColor  # Import QColor for handling colors

import pandas as pd

import csv
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsMarkerSymbol,
    QgsLineSymbol, QgsVectorFileWriter
)
from PyQt5.QtCore import QVariant
from matplotlib import cm  # Import colormap functionality from matplotlib
from matplotlib.colors import to_hex  # Convert RGB to hex
from PyQt5.QtGui import QColor  # Import QColor for hanand teh dling colors

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsMarkerSymbol,
    QgsLineSymbol, QgsVectorFileWriter
)
from PyQt5.QtCore import QVariant
from matplotlib import cm  # Import colormap functionality from matplotlib
from matplotlib.colors import to_hex  # Convert RGB to hex
from PyQt5.QtGui import QColor  # Import QColor for handling colors

def CreateSpoofLayersAndClusters(events_df, events_clusters, layer_name, output_shapefile=None, show_none_clustered_events=False):
    """
    Creates QGIS layers with points and lines from an events DataFrame and draws lines between them.
    The second point is placed in a separate layer and is twice as large.
    Lines are drawn between the first and second points, and between the second and third points.
    
    Both point layers and the line layer are categorized by 'cluster', with point 2 being larger.
    
    Parameters:
    - events_df: DataFrame containing event information with columns:
        ['start_lat_pre', 'start_lon_pre', 'start_lat', 'start_lon', 
         'end_lat', 'end_lon', 'start_time', 'end_time', 'cluster_num', 'name']
    - layer_name: Name of the QGIS layers.
    - output_shapefile: Path to save the layers as shapefiles (optional).
    """

    # Remove existing layers with the same names
    for layer in QgsProject.instance().mapLayers().values():
        if layer.name() in [layer_name + '_spoof_start_end_points', layer_name + '_spoof_target', 
                            layer_name + '_lines', layer_name + '_polygons']:
            QgsProject.instance().removeMapLayer(layer.id())

    # Create memory layers for points, lines, and polygons
    point_layer_1_3 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_start_end_points', 'memory')
    provider_1_3 = point_layer_1_3.dataProvider()

    point_layer_2 = QgsVectorLayer('Point?crs=EPSG:4326', layer_name + '_spoof_target', 'memory')
    provider_2 = point_layer_2.dataProvider()

    line_layer = QgsVectorLayer('LineString?crs=EPSG:4326', layer_name + '_lines', 'memory')
    line_provider = line_layer.dataProvider()

    # Create memory layer for polygons
    polygon_layer = QgsVectorLayer('Polygon?crs=EPSG:4326', layer_name + '_polygons', 'memory')
    polygon_provider = polygon_layer.dataProvider()

    # Define fields for the point and line layers, including 'name'
    fields = [
        QgsField('cluster', QVariant.String),
        QgsField('start_time', QVariant.String),
        QgsField('end_time', QVariant.String),
        QgsField('type', QVariant.String),
        QgsField('name', QVariant.String)  # Added name field
    ]
    provider_1_3.addAttributes(fields)
    provider_2.addAttributes(fields)
    line_provider.addAttributes([QgsField('cluster', QVariant.String)])
    polygon_provider.addAttributes(fields)  # Add same fields to polygon layer
    point_layer_1_3.updateFields()
    point_layer_2.updateFields()
    line_layer.updateFields()
    polygon_layer.updateFields()

    cluster_nums = []    
    for j, cluster in enumerate(events_clusters):
        cluster_num = cluster['cluster_num']
        indices = cluster['events_df_index']  # Get the list of indices for this cluster

        cluster_nums.append(cluster_num)

        for i, index in enumerate(indices):
            row = events_df.loc[index]  # Use loc to access the event from events_df          
            try:
                # Skip cluster -1 if not displaying none-clustered events
                if not show_none_clustered_events and cluster_num == -1:
                    continue

                # Point 1: start_lat_pre, start_lon_pre
                start_lat_pre = float(row['start_lat_pre']) if row['start_lat_pre'] else None
                start_lon_pre = float(row['start_lon_pre']) if row['start_lat_pre'] else None
                
                # Point 2: start_lat, start_lon (this will be in a separate layer)
                start_lat = float(row['start_lat']) if row['start_lat'] else None
                start_lon = float(row['start_lon']) if row['start_lon'] else None
                
                # Point 3: end_lat, end_lon
                end_lat = float(row['end_lat']) if row['end_lat'] else None
                end_lon = float(row['end_lon']) if row['end_lon'] else None
                
                if not (start_lat_pre and start_lon_pre and start_lat and start_lon and end_lat and end_lon):
                    continue  # Skip rows with missing or invalid data
                
                # Create features for points 1 and 3
                point1 = QgsFeature()
                point1.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(start_lon_pre, start_lat_pre)))
                point1.setAttributes([cluster_num, row['start_time'].strftime("%Y-%m-%d %H:%M:%S"), 
                                      row['end_time'].strftime("%Y-%m-%d %H:%M:%S"), row['type'], row['name']])  # Include name
                provider_1_3.addFeature(point1)

                point3 = QgsFeature()
                point3.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(end_lon, end_lat)))
                point3.setAttributes([cluster_num, row['start_time'].strftime("%Y-%m-%d %H:%M:%S"), 
                                      row['end_time'].strftime("%Y-%m-%d %H:%M:%S"), row['type'], row['name']])  # Include name
                provider_1_3.addFeature(point3)

                # Create a feature for point 2
                point2 = QgsFeature()
                point2.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(start_lon, start_lat)))
                point2.setAttributes([cluster_num, row['start_time'].strftime("%Y-%m-%d %H:%M:%S"), 
                                      row['end_time'].strftime("%Y-%m-%d %H:%M:%S"), row['type'], row['name']])  # Include name
                provider_2.addFeature(point2)

                # Create a line between Point 1 and Point 2
                line1 = QgsFeature()
                line1.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(start_lon_pre, start_lat_pre),
                                                              QgsPointXY(start_lon, start_lat)]))
                line1.setAttributes([cluster_num])
                line_provider.addFeature(line1)

                # Create a line between Point 3 and Point 2
                line2 = QgsFeature()
                line2.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(end_lon, end_lat),
                                                              QgsPointXY(start_lon, start_lat)]))
                line2.setAttributes([cluster_num])
                line_provider.addFeature(line2)

                # Create polygon from cluster data
                if 'polygon' in cluster and isinstance(cluster['polygon'], pd.DataFrame):
                    polygon_points = []
                    for _, point in cluster['polygon'].iterrows():
                        lat = point['lat']
                        lon = point['lon']
                        polygon_points.append(QgsPointXY(float(lon), float(lat)))

                    if polygon_points:  # Ensure we have points to create a polygon
                        polygon = QgsFeature()
                        polygon_geom = QgsGeometry.fromPolygonXY([polygon_points])
                        polygon.setGeometry(polygon_geom)
                        polygon.setAttributes([cluster_num, None, None, None, row['name']])  # Include name in polygon attributes
                        polygon_provider.addFeature(polygon)

            except ValueError as e:
                print(f"Error processing row {index}: {e}")
                continue

    # Add the point, line, and polygon layers to the QGIS project
    QgsProject.instance().addMapLayer(point_layer_1_3)
    QgsProject.instance().addMapLayer(point_layer_2)
    QgsProject.instance().addMapLayer(line_layer)
    QgsProject.instance().addMapLayer(polygon_layer)  # Add polygon layer

    # Create a color map that will be used for points, lines, and polygons
    categories_1_3 = []
    categories_2 = []
    line_categories = []
    polygon_categories = []  # For polygon layer
    
    # Create a colormap from matplotlib
    colormap = cm.get_cmap('tab20', len(cluster_nums))  # Using 'tab20' for distinct colors

    for i, cluster_num in enumerate(cluster_nums):
        # Create symbols for points 1 and 3
        symbol_1_3 = QgsMarkerSymbol.defaultSymbol(point_layer_1_3.geometryType())
        symbol_2 = QgsMarkerSymbol.defaultSymbol(point_layer_2.geometryType())
        line_symbol = QgsLineSymbol.defaultSymbol(line_layer.geometryType())
        polygon_symbol = QgsFillSymbol.createSimple({'color': 'transparent', 'outline_color': to_hex(colormap(i))})  # Polygon symbol

        color = QColor(to_hex(colormap(i)))  # Convert hex to QColor

        # Set colors for symbols
        symbol_1_3.symbolLayer(0).setColor(color)
        symbol_2.symbolLayer(0).setColor(color)
        symbol_2.setSize(10)  # Set larger size for point 2
        line_symbol.symbolLayer(0).setColor(color)

        # Create categories for points and lines
        category_1_3 = QgsRendererCategory(str(cluster_num), symbol_1_3, str(cluster_num))
        category_2 = QgsRendererCategory(str(cluster_num), symbol_2, str(cluster_num))
        line_category = QgsRendererCategory(str(cluster_num), line_symbol, str(cluster_num))
        polygon_category = QgsRendererCategory(str(cluster_num), polygon_symbol, str(cluster_num))  # For polygons

        categories_1_3.append(category_1_3)
        categories_2.append(category_2)
        line_categories.append(line_category)
        polygon_categories.append(polygon_category)

    # Apply the categorized renderers to the point, line, and polygon layers
    categorized_renderer_1_3 = QgsCategorizedSymbolRenderer('cluster', categories_1_3)
    point_layer_1_3.setRenderer(categorized_renderer_1_3)

    categorized_renderer_2 = QgsCategorizedSymbolRenderer('cluster', categories_2)
    point_layer_2.setRenderer(categorized_renderer_2)

    line_categorized_renderer = QgsCategorizedSymbolRenderer('cluster', line_categories)
    line_layer.setRenderer(line_categorized_renderer)

    polygon_categorized_renderer = QgsCategorizedSymbolRenderer('cluster', polygon_categories)
    polygon_layer.setRenderer(polygon_categorized_renderer)  # Apply to polygon layer

    # Optionally save the layers as shapefiles
    if output_shapefile:
        point_output_1_3 = output_shapefile + '_spoof_start_end_points.shp'
        point_output_2 = output_shapefile + '_spoof_target.shp'
        line_output = output_shapefile + '_lines.shp'
        polygon_output = output_shapefile + '_polygons.shp'  # For polygons

        QgsVectorFileWriter.writeAsVectorFormat(point_layer_1_3, point_output_1_3, "UTF-8", point_layer_1_3.crs(), "ESRI Shapefile")
        QgsVectorFileWriter.writeAsVectorFormat(point_layer_2, point_output_2, "UTF-8", point_layer_2.crs(), "ESRI Shapefile")
        QgsVectorFileWriter.writeAsVectorFormat(line_layer, line_output, "UTF-8", line_layer.crs(), "ESRI Shapefile")
        QgsVectorFileWriter.writeAsVectorFormat(polygon_layer, polygon_output, "UTF-8", polygon_layer.crs(), "ESRI Shapefile")  # Save polygon layer

        print(f'Successfully saved point layers to {point_output_1_3} and {point_output_2}')
        print(f'Successfully saved line layer to {line_output}')
        print(f'Successfully saved polygon layer to {polygon_output}')
    else:
        print('Layers added to QGIS project but not saved to disk.')

