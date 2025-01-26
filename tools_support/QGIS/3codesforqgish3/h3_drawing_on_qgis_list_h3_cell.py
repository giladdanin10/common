
import geopandas as gpd
from shapely.geometry import Polygon
import h3
import geopandas as gpd
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface 



def h3_to_geodataframe(h3_indexes, crs="EPSG:4326"):
    """
    Converts a list of H3 indexes to a GeoPandas GeoDataFrame with polygon geometries.

    Parameters:
        h3_indexes (list): List of H3 indexes.
        crs (str): Coordinate reference system for the GeoDataFrame (default: EPSG:4326).

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with H3 indexes and their corresponding geometries.
    """
    try:
        def h3_to_polygon(h3_index):
            boundary = h3.cell_to_boundary(h3_index)  # Get boundary as a tuple of lat/lng
            
            # Switch coordinates from (x, y) to (y, x)
            # the switch is needed to match geopandas is using (x, y) format and h3 is using (y, x) format 
            switched_boundary = [(y, x) for x, y in boundary]
    
            return Polygon(switched_boundary)
            
            
    except Exception as e:
        raise Exception(f"Error processing h3_to_geodataframe -> h3_to_polygon error: {str(e)}")

    try:
        # Convert H3 indexes to polygons
        geometries = [h3_to_polygon(h3_index) for h3_index in h3_indexes]
    except Exception as e:
        raise Exception(f"Error processing h3_to_geodataframe -> h3_to_polygon error: {str(e)}")
    
    try:
        print(geometries)
        # Create a GeoDataFrame
        gdf = gpd.GeoDataFrame({'h3_index': h3_indexes, 'geometry': geometries}, crs=crs)
        return gdf
    except Exception as e:
        raise Exception(f"Error processing h3_to_geodataframe -> Create a GeoDataFrame error: {str(e)}")

def upload_geodataframe_to_qgis(gdf, layer_name="GeoDataFrame Layer"):
    """
    Uploads a GeoPandas GeoDataFrame to QGIS as a new layer.

    Parameters:
        gdf (geopandas.GeoDataFrame): The GeoDataFrame to upload.
        layer_name (str): Name for the QGIS layer.
    """
    # Check if the GeoDataFrame is valid
    if gdf.empty:
        raise ValueError("The GeoDataFrame is empty and cannot be uploaded.")

    print("Columns in GeoDataFrame:", gdf.columns)

    # Determine the layer geometry type based on GeoDataFrame geometry
    if gdf.geom_type.iloc[0] == "Polygon" or gdf.geom_type.iloc[0] == "MultiPolygon":
        geometry_type = "Polygon"
    elif gdf.geom_type.iloc[0] == "Point":
        geometry_type = "Point"
    elif gdf.geom_type.iloc[0] == "LineString":
        geometry_type = "LineString"
    else:
        raise ValueError("Unsupported geometry type in GeoDataFrame.")

    # Create an empty vector layer in memory
    layer = QgsVectorLayer(f"{geometry_type}?crs=epsg:4326", layer_name, "memory")
    provider = layer.dataProvider()

    # Add fields from GeoDataFrame to QGIS layer
    for column in gdf.columns:
        if column != "geometry":  # Exclude the geometry column
            provider.addAttributes([QgsField(column, QVariant.String)])  # Adjust QVariant type as needed
    layer.updateFields()

    # Fetch the field names for the QGIS layer
    field_names = [field.name() for field in provider.fields()]

    # Add features to the layer from the GeoDataFrame
    for _, row in gdf.iterrows():
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(row.geometry.wkt()))  # Set the geometry from GeoDataFrame

        # Ensure attributes are set for matching fields
        attributes = []
        for field in field_names:
            value = row[field] if field in row else None
            attributes.append(str(value) if value is not None else None)
        feature.setAttributes(attributes)

        # Add the feature to the provider
        provider.addFeature(feature)

    
    # Update the layer extent
    layer.updateExtents()

    # Add the layer to the current QGIS project
    QgsProject.instance().addMapLayer(layer)
    print(f"Layer '{layer_name}' added to QGIS!")
    # Get the extent and transform it if needed
    extent = layer.extent()
    canvas = iface.mapCanvas()

    # Ensure the extent is in the same CRS as the map canvas
    if canvas.mapSettings().destinationCrs() != layer.crs():
        transform = QgsCoordinateTransform(layer.crs(), canvas.mapSettings().destinationCrs(), QgsProject.instance())
        extent = transform.transformBoundingBox(extent)

    # Add a small buffer for better visibility
    extent.grow(extent.width() * 0.1)

    # Set the extent and refresh
    canvas.setExtent(extent)
    canvas.refresh()

h3_cell_list= ['8b2db2b2584dfff']
layer_name="My H3 Layer"
try:
    # Convert H3 cell to geopadas-  dataframe (WGS84 coordinate system)
    gdf = h3_to_geodataframe(h3_cell_list)
    print(f"list h3 cells converted to geodataframe successfully!")
    # Upload the GeoDataFrame to QGIS 
    upload_geodataframe_to_qgis(gdf, layer_name="My H3 Layer")
except Exception as e:
    raise Exception(f"Error reading file: {str(e)}")


