import os
import csv
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsMarkerSymbol,
    QgsLineSymbol, QgsVectorFileWriter, QgsCoordinateReferenceSystem
)
from PyQt5.QtCore import QVariant
from matplotlib import cm
from matplotlib.colors import to_hex
from PyQt5.QtGui import QColor

class QGIS:
    @staticmethod
    def CreateVesselPathLayer(layer_name, data_file, location_columns_dic={'lat': 'latitude', 'lon': 'longitude'}, classification_node=None):
        try:
            # Remove any existing layers with the same name
            existing_layers = QgsProject.instance().mapLayersByName(layer_name)
            if existing_layers:
                for layer in existing_layers:
                    QgsProject.instance().removeMapLayer(layer.id())
                print(f"Deleted existing layer(s) with the name '{layer_name}'.")

            # Check if the data file exists
            if not os.path.exists(data_file):
                print(f"Error: Data file '{data_file}' not found.")
                return
            
            # Get latitude and longitude column names from the dictionary
            lat_col = location_columns_dic.get('lat', 'latitude')
            lon_col = location_columns_dic.get('lon', 'longitude')

            # Define the URI for the delimited text layer
            uri = f"file:///{data_file}?delimiter=,&xField={lon_col}&yField={lat_col}"

            # Load the data file as a delimited text layer
            layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
            if not layer.isValid():
                print(f"Error: Failed to load layer from file '{data_file}'.")
                return

            # Set CRS to WGS 84 (EPSG:4326)
            layer.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))

            # Add the layer to the QGIS project
            QgsProject.instance().addMapLayer(layer)
            print(f"Layer '{layer_name}' created from file '{data_file}'.")

            # Optional classification
            if classification_node:
                if classification_node not in [field.name() for field in layer.fields()]:
                    print(f"Error: Classification field '{classification_node}' not found in the data.")
                    return
                
                categories = []
                seen_values = set()

                for feature in layer.getFeatures():
                    value = feature[classification_node]
                    if value not in seen_values:
                        symbol = QgsMarkerSymbol.defaultSymbol(layer.geometryType())
                        category = QgsRendererCategory(value, symbol, str(value))
                        categories.append(category)
                        seen_values.add(value)

                renderer = QgsCategorizedSymbolRenderer(classification_node, categories)
                layer.setRenderer(renderer)
                print(f"Layer '{layer_name}' classified by '{classification_node}'.")

            # Refresh the project (No iface interaction in standalone scripts)
            layer.triggerRepaint()
            
        except Exception as e:
            print(f"Error occurred: {e}")

    @staticmethod
    def RestartProject():
        try:
            # Remove all layers from the project except for OpenStreetMap layer
            osm_layer_name = "OpenStreetMap"
            existing_layers = QgsProject.instance().mapLayers().values()
            osm_layer_exists = any(layer.name() == osm_layer_name for layer in existing_layers)

            # Remove all existing layers except OpenStreetMap
            for layer in existing_layers:
                if layer.name() != osm_layer_name:
                    QgsProject.instance().removeMapLayer(layer.id())
            
            # If OpenStreetMap layer does not exist, add it
            if not osm_layer_exists:
                street_map_layer = QgsRasterLayer("type=xyz|url=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", osm_layer_name)
                if street_map_layer.isValid():
                    QgsProject.instance().addMapLayer(street_map_layer)
                    street_map_layer.setOpacity(1.0)
                    print("Street map layer added.")
                else:
                    print("Failed to add street map layer.")

        except Exception as e:
            print(f"Error occurred: {e}")
