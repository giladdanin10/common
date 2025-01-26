import geopandas as gpd
from shapely.geometry import Polygon
import h3
import pandas as pd
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsCoordinateTransform

def h3_to_geodataframe_from_file(file_path, column_name="h3_index", crs="EPSG:4326"):
    """
    Reads a file (JSON or CSV), extracts H3 indexes and additional factual columns,
    and converts them into a GeoDataFrame.

    Parameters:
        file_path (str): Path to the JSON or CSV file.
        column_name (str): Name of the column containing H3 indexes (default: "h3_index").
        crs (str): Coordinate reference system for the GeoDataFrame (default: EPSG:4326).

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with H3 indexes, additional columns, and their geometries.
    """
    try:
        # Load the file based on its extension
        if file_path.endswith(".json"):
            df = pd.read_json(file_path)
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a JSON or CSV file.")

        # Ensure the column exists in the file
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the file.")

        # Extract the H3 indexes
        h3_indexes = df[column_name].tolist()

        def h3_to_polygon(h3_index):
            # Convert H3 index to a polygon and switch (x, y) to (y, x)
            boundary = h3.cell_to_boundary(h3_index)
            switched_boundary = [(y, x) for x, y in boundary]
            return Polygon(switched_boundary)

        # Convert H3 indexes to geometries
        geometries = [h3_to_polygon(h3_index) for h3_index in h3_indexes]

        # Add the geometries column to the DataFrame
        df["geometry"] = geometries

        # Create a GeoDataFrame from the DataFrame
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=crs)
        return gdf

    except Exception as e:
        raise Exception(f"Error in h3_to_geodataframe_from_file: {str(e)}")

def upload_geodataframe_to_qgis(gdf, layer_name="GeoDataFrame Layer"):
    """
    Uploads a GeoPandas GeoDataFrame to QGIS as a new layer.

    Parameters:
        gdf (geopandas.GeoDataFrame): The GeoDataFrame to upload.
        layer_name (str): Name for the QGIS layer.
    """
    if gdf.empty:
        raise ValueError("The GeoDataFrame is empty and cannot be uploaded.")

    # Determine the layer geometry type
    if gdf.geom_type.iloc[0] == "Polygon" or gdf.geom_type.iloc[0] == "MultiPolygon":
        geometry_type = "Polygon"
    else:
        raise ValueError("Unsupported geometry type in GeoDataFrame.")

    # Create an empty vector layer in memory
    layer = QgsVectorLayer(f"{geometry_type}?crs=epsg:4326", layer_name, "memory")
    provider = layer.dataProvider()

    # Add fields to the QGIS layer
    for column in gdf.columns:
        if column != "geometry":
            provider.addAttributes([QgsField(column, QVariant.String)])
    layer.updateFields()

    # Add features to the layer
    field_names = [field.name() for field in provider.fields()]
    for _, row in gdf.iterrows():
        feature = QgsFeature()
        # feature.setGeometry(QgsGeometry.fromWkt(row.geometry.to_wkt()))
        feature.setGeometry(QgsGeometry.fromWkt(row.geometry.wkt))

        feature.setAttributes([str(row[field]) if field in row else None for field in field_names])
        provider.addFeature(feature)

    # Update the layer extent
    layer.updateExtents()

    # Add the layer to the QGIS project
    QgsProject.instance().addMapLayer(layer)

    # Zoom to the layer
    canvas = iface.mapCanvas()
    extent = layer.extent()
    if canvas.mapSettings().destinationCrs() != layer.crs():
        transform = QgsCoordinateTransform(layer.crs(), canvas.mapSettings().destinationCrs(), QgsProject.instance())
        extent = transform.transformBoundingBox(extent)
    extent.grow(extent.width() * 0.1)
    canvas.setExtent(extent)
    canvas.refresh()
    print(f"Layer '{layer_name}' added and zoomed in QGIS!")


try:
    # Specify the path to your JSON or CSV file
    file_path = r"C:\work\code\common\tools_support\QGIS\3codesforqgish3\testfiles\test.csv"  # Replace with your file path
    column_name = "h3_index"  # Column name containing H3 indexes

    # Convert H3 indexes and additional factual columns into a GeoDataFrame
    gdf = h3_to_geodataframe_from_file(file_path, column_name)

    # Upload the GeoDataFrame to QGIS
    upload_geodataframe_to_qgis(gdf, layer_name="My H3 Layer1")
except Exception as e:
    print(f"Error: {str(e)}")
