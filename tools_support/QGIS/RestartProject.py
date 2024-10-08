from qgis.core import QgsProject
from qgis.core import QgsRasterLayer

def RestartProject():
    """
    Removes all layers from the current QGIS project except for the OpenStreetMap layer
    and adds or refreshes the street map layer.
    """
    # Check if the OpenStreetMap layer already exists
    osm_layer_name = "OpenStreetMap"
    existing_layers = QgsProject.instance().mapLayers().values()
    osm_layer_exists = any(layer.name() == osm_layer_name for layer in existing_layers)

    # Remove all existing layers except the OpenStreetMap layer
    for layer in existing_layers:
        if layer.name() != osm_layer_name:
            QgsProject.instance().removeMapLayer(layer.id())
    
    # If the OpenStreetMap layer does not exist, add it
    if not osm_layer_exists:
        street_map_layer = QgsRasterLayer("type=xyz|url=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", osm_layer_name)
        
        # Check if the layer is valid
        if not street_map_layer.isValid():
            print("Failed to add street map layer.")
        else:
            # Add the layer to the project
            QgsProject.instance().addMapLayer(street_map_layer)
            street_map_layer.setOpacity(1.0)  # Set the opacity to fully visible
            street_map_layer.setVisible(True)  # Ensure the layer is visible
            print("Street map layer added.")

    # Refresh the map canvas to ensure the layer appears
    iface.mapCanvas().refresh()
