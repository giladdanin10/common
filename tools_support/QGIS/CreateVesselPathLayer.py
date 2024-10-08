import os

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
