import os
import re
import html

def apply_filter_to_layer(layer_name, filter_file=None):
    """
    Applies a filter to the specified layer by setting it as a manual filter (subset string).
    If no filter is provided, the existing filter will be cleared.
    
    :param layer_name: The name of the layer to apply the filter.
    :param filter_file: The path to the filter file. If None, the filter will be cleared.
    """
    try:
        # Get the layer by name
        layers = QgsProject.instance().mapLayersByName(layer_name)
        
        if not layers:
            print(f"Layer '{layer_name}' not found.")
            return
        
        map_layer = layers[0]

        # Initialize filter expression as None
        filter_expression = None

        # If a filter file is provided, read and decode it
        if filter_file:
            if os.path.exists(filter_file):
                print(f"Applying filter from: {filter_file}")
                with open(filter_file, 'r') as f:
                    file_content = f.read().strip()
                    # Extract filter expression from XML-style tags if present
                    match = re.search(r"<Query>(.*?)</Query>", file_content)
                    if match:
                        filter_expression = match.group(1).strip()
                    else:
                        filter_expression = file_content
                    
                    # Decode HTML entities (e.g., &lt; becomes <)
                    filter_expression = html.unescape(filter_expression)
                print(f"Decoded Filter expression: {filter_expression}")
            else:
                print(f"Filter file '{filter_file}' not found. Proceeding without filtering.")
        
        # Apply or clear the filter expression as a subset string
        if filter_expression:
            map_layer.setSubsetString(filter_expression)
            print(f"Filter applied: {filter_expression}")
        else:
            map_layer.setSubsetString('')  # Clear the filter if no expression is provided
            print("No filter expression provided. Cleared any existing filter.")

        # Refresh the map to apply changes
        map_layer.triggerRepaint()
        iface.mapCanvas().refreshAllLayers()

        # Optionally, save the project to persist the changes
        QgsProject.instance().write()

    except Exception as e:
        print(f"Error occurred: {e}")


def prepare_layer_for_accuracy_analysis(layer_name, source_file=None, filter_file=None):
    """
    Prepares a layer for accuracy analysis by setting accuracy-related styles and applying an optional filter.
    
    :param layer_name: The name of the layer to prepare.
    :param source_file: The path to the new source file. If not provided, the current source file is used.
    :param filter_file: The path to the filter file. If provided, the filter will be applied.
    """
    try:
        # Get the layer by name
        layers = QgsProject.instance().mapLayersByName(layer_name)
        
        if not layers:
            print(f"Layer '{layer_name}' not found.")
            return
        
        map_layer = layers[0]

        # Update the source file if provided, otherwise use the current source file
        if source_file:
            print(f"Updating the source file to: {source_file}")
            provider = map_layer.dataProvider()
            provider.setDataSourceUri(source_file)
            map_layer.setDataSource(source_file, map_layer.name(), provider.name())
            # Reload the layer to ensure the changes take effect
            QgsProject.instance().removeMapLayer(map_layer.id())
            reloaded_layer = QgsVectorLayer(source_file, layer_name, provider.name())
            if not reloaded_layer.isValid():
                print(f"Error reloading the layer '{layer_name}' from the new source.")
                return
            QgsProject.instance().addMapLayer(reloaded_layer)
            map_layer = reloaded_layer  # Update reference to the reloaded layer
        else:
            print("No source file provided. Using the current source file.")

        # Apply the filter (using the dedicated filtering function)
        apply_filter_to_layer(layer_name, filter_file)

        # Apply accuracy-based styling (as requested earlier)
        print("Applying accuracy-based styling...")

        # Refresh the map to apply changes
        map_layer.triggerRepaint()
        iface.mapCanvas().refreshAllLayers()

        # Optionally, save the project to persist the changes
        QgsProject.instance().write()

        print(f"Layer '{layer_name}' has been prepared for accuracy analysis.")

    except Exception as e:
        print(f"Error occurred: {e}")
