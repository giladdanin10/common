import pandas as pd
import h3
from shapely.geometry import Polygon
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsGraduatedSymbolRenderer,
    QgsRendererRange,
    QgsSymbol,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

def PresentH3Feature(csv_file, h3_index_column, present_column):
    """
    Reads a CSV file with H3 indexes, processes it, and presents the specified column on QGIS
    with a graduated color style based on the column's values.

    Parameters:
        csv_file (str): Path to the CSV file containing H3 indexes and additional data.
        h3_index_column (str): Name of the column containing H3 indexes.
        present_column (str): Column to display on the QGIS layer and use for coloring.
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_file)

        # Ensure the required columns exist
        if h3_index_column not in df.columns:
            raise ValueError(f"Column '{h3_index_column}' not found in the file.")
        if present_column not in df.columns:
            raise ValueError(f"Column '{present_column}' not found in the file.")

        # Convert H3 indexes to geometries
        def h3_to_polygon(h3_index):
            boundary = h3.cell_to_boundary(h3_index)
            # Convert (lat, lng) to (lng, lat) for Shapely
            converted_boundary = [(lng, lat) for lat, lng in boundary]
            return Polygon(converted_boundary)

        df["geometry"] = df[h3_index_column].apply(h3_to_polygon)

        # Create a vector layer in QGIS
        layer = QgsVectorLayer("Polygon?crs=epsg:4326", "H3 Layer", "memory")
        provider = layer.dataProvider()

        # Add fields to the layer
        provider.addAttributes([
            QgsField(h3_index_column, QVariant.String),
            QgsField(present_column, QVariant.Double)
        ])
        layer.updateFields()

        # Add features to the layer
        for _, row in df.iterrows():
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromWkt(row.geometry.wkt))
            feature.setAttributes([row[h3_index_column], row[present_column]])
            provider.addFeature(feature)

        # Update the layer extent
        layer.updateExtents()

        # Define graduated color ranges
        min_value = df[present_column].min()
        max_value = df[present_column].max()
        interval = (max_value - min_value) / 5  # Divide into 5 classes
        ranges = []
        for i in range(5):
            lower_bound = min_value + i * interval
            upper_bound = min_value + (i + 1) * interval
            label = f"{lower_bound:.2f} - {upper_bound:.2f}"
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            
            # Calculate RGB gradient color
            red = int(255 * (i / 4))  # Gradient from 0 to 255 (low to high)
            blue = int(255 * (1 - (i / 4)))  # Gradient from 255 to 0
            color = QColor(red, 0, blue)  # Red to blue gradient
            symbol.setColor(color)
            
            ranges.append(QgsRendererRange(lower_bound, upper_bound, symbol, label))

        # Apply graduated renderer
        renderer = QgsGraduatedSymbolRenderer(present_column, ranges)
        renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
        layer.setRenderer(renderer)

        # Add the layer to the QGIS project
        QgsProject.instance().addMapLayer(layer)

        # Zoom to the layer
        iface.mapCanvas().setExtent(layer.extent())
        iface.mapCanvas().refresh()

        print(f"Layer added successfully with graduated color styling for '{present_column}'.")

    except Exception as e:
        print(f"Error in PresentH3Feature: {e}")


# Example usage
csv_file = r"C:\work\code\TipAndQue-algo\src\test\jamming\pre_process\aircraft_data_20240401\h3_features_df_16.csv"

present_column = "nac_p_max"  # Replace with the column to present
h3_index_column = "level_0"
PresentH3Feature(csv_file,h3_index_column,present_column)
