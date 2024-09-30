import os

def CreateVesselPathLayer(layer_name, data_file, classification_node=None):
    """
    Creates a QGIS delimited text layer from a data file, deletes any existing layers with the same name, 
    and optionally classifies it based on a specified field, maintaining the order from the original file.
    
    :param layer_name: The name to assign to the new layer.
    :param data_file: The path to the data file (e.g., CSV).
    :param classification_node: The field by which the layer will be optionally classified. If None, no classification is applied.
    """
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
        
        # Define the URI for the delimited text layer, assuming the data has latitude and longitude fields
        uri = f"file:///{data_file}?delimiter=,&xField=longitude&yField=latitude"

        # Load the data file as a delimited text layer
        layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
        
        if not layer.isValid():
            print(f"Error: Failed to load layer from file '{data_file}'.")
            return

        # Set CRS to WGS 84 (EPSG:4326) for latitude/longitude data
        layer.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))

        # Add the layer to the QGIS project
        QgsProject.instance().addMapLayer(layer)
        print(f"Layer '{layer_name}' created from file '{data_file}'.")

        # Optional classification step
        if classification_node:
            # Get the attribute list and check if the classification node exists
            if classification_node not in [field.name() for field in layer.fields()]:
                print(f"Error: Classification field '{classification_node}' not found in the data.")
                return
            
            # Create a categorized renderer based on the classification node
            categories = []
            seen_values = set()  # To avoid duplicates

            # Iterate through features in the original order of the file
            for feature in layer.getFeatures():
                value = feature[classification_node]
                if value not in seen_values:
                    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                    category = QgsRendererCategory(value, symbol, str(value))
                    categories.append(category)
                    seen_values.add(value)

            renderer = QgsCategorizedSymbolRenderer(classification_node, categories)
            
            # Apply the renderer to the layer
            layer.setRenderer(renderer)
            print(f"Layer '{layer_name}' classified by '{classification_node}' in original order.")

        # Zoom to the layer's extent to make it visible
        if layer.extent().isEmpty():
            print(f"Layer '{layer_name}' has no visible extent (no data found).")
        else:
            iface.mapCanvas().setExtent(layer.extent())
            iface.mapCanvas().refresh()

        # Refresh the map and legend
        layer.triggerRepaint()
        iface.mapCanvas().refreshAllLayers()
        iface.layerTreeView().refreshLayerSymbology(layer.id())

    except Exception as e:
        print(f"Error occurred: {e}")
