
# from geopy.point import Point
import geopy as geopy
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from ipyleaflet import Map, GeoData, Marker, DivIcon, GeoJSON, WidgetControl, Polygon,DivIcon
from shapely.geometry import Polygon as ShapelyPolygon
from ipywidgets import Label, VBox
from ipyleaflet import Map, TileLayer
import re

from ipywidgets import HTML
import random
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

import numpy as np
import pandas as pd


def calculate_distance(p1, p2):
    """
    Calculate the great-circle distance and the approximate dx and dy (in km) between two points on the Earth.
    
    Parameters:
    p1 (list or tuple): The [latitude, longitude] pair of the first point.
    p2 (list or tuple): The [latitude, longitude] pair of the second point.
    
    Returns:
    dict: A dictionary containing the great-circle distance (dr_km), dx_km, and dy_km.
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad, long1_rad = np.radians(p1)
    lat2_rad, long2_rad = np.radians(p2)
    
    # Calculate differences in latitude and longitude (in radians)
    dlat = lat2_rad - lat1_rad
    dlon = long2_rad - long1_rad
    
    # Haversine formula to calculate great-circle distance (dr_km)
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    dr_km = R * c
    
    # Calculate dx_km (approximation for longitude distance)
    dx_km = R * dlon * np.cos((lat1_rad + lat2_rad) / 2)
    
    # Calculate dy_km (approximation for latitude distance)
    dy_km = R * dlat
    
    return dr_km



def lat_long_to_km(df, lat_col='latitude', long_col='longitude'):
    # Earth's radius in kilometers
    R = 6371.0

    # Convert degrees to radians
    df['lat_rad'] = np.radians(df[lat_col])
    df['long_rad'] = np.radians(df[long_col])

    # Calculate differences in latitude and longitude (in radians)
    df['dlat'] = df['lat_rad'].diff()
    df['dlon'] = df['long_rad'].diff()

    # Haversine formula to calculate dr_km (great-circle distance)
    a = np.sin(df['dlat'] / 2)**2 + np.cos(df['lat_rad']) * np.cos(df['lat_rad']) * np.sin(df['dlon'] / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    df['dr_km'] = R * c

    # Calculate dx_km (approximation for longitude distance)
    df['dx_km'] = R * df['dlon'] * np.cos(df['lat_rad'])

    # Calculate dy_km (approximation for latitude distance)
    df['dy_km'] = R * df['dlat']

    # Drop intermediate columns
    df.drop(columns=['lat_rad', 'long_rad', 'dlat', 'dlon'], inplace=True)

    return df

# Example DataFrame usage
data = {
    'latitude': [52.2296756, 41.8919300, 50.850340, 48.856614],
    'longitude': [21.0122287, 12.5113300, 4.351710, 2.352222]
}
df = pd.DataFrame(data)

df_with_distances = lat_long_to_km(df)
print(df_with_distances[['dx_km', 'dy_km', 'dr_km']])



class map_display:
    @staticmethod
    def df_to_gdf(df: pd.DataFrame, lat_col: str = 'latitude', lon_col: str = 'longitude') -> gpd.GeoDataFrame:
        """
        Converts a pandas DataFrame to a GeoDataFrame.

        Parameters:
        - df (pd.DataFrame): The DataFrame to convert.
        - lat_col (str): The name of the latitude column. Default is 'latitude'.
        - lon_col (str): The name of the longitude column. Default is 'longitude'.

        Returns:
        - gpd.GeoDataFrame: A GeoDataFrame with geometry column created from lat/lon.
        """
        return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]))

    @staticmethod
    def add_polygons_to_map(m: Map, polygons: List[Dict], fill_polygons: bool) -> None:
        """
        Adds polygons to the map.

        Parameters:
        - m (Map): The ipyleaflet Map object to add polygons to.
        - polygons (list): A list of dictionaries, each containing 'coordinates' (list of (lat, lon) tuples) and 'color' (optional, default 'blue').
        - fill_polygons (bool): If True, the polygons are filled. If False, only the borders are drawn.
        """
        for poly in polygons:
            coords = poly['coordinates']
            color = poly.get('color', 'blue')
            polygon = Polygon(
                locations=coords,
                color=color,
                fill_color=color if fill_polygons else 'transparent',
                fill_opacity=0.5 if fill_polygons else 0,
                weight=2
            )
            m.add_layer(polygon)

    @staticmethod
    def create_grid_layer() -> Tuple[GeoJSON, List[Marker]]:
        """
        Creates a grid layer with latitude and longitude lines and labels.

        Returns:
        - grid_layer (GeoJSON): The GeoJSON layer with grid lines.
        - markers (list): A list of Marker objects for the grid labels.
        """
        lines = {
            "type": "FeatureCollection",
            "features": []
        }

        markers = []

        # Create latitude lines and labels
        for lat in range(-90, 91, 10):  # Increment by 20 for every second cross-section
            lines["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lon in range(-180, 181, 10)]
                },
                "properties": {
                    "name": f"{lat}° lat"
                }
            })
            if lat != 0:  # Skip equator label as an example
                label = f"<div style='color: blue; font-size: 10px; background-color: white;'>{lat}°</div>"
                icon = DivIcon(html=label)
                marker = Marker(location=(lat, 0), icon=icon)
                markers.append(marker)

        # Create longitude lines and labels
        for lon in range(-180, 181, 10):  # Increment by 20 for every second cross-section
            lines["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat in range(-90, 91, 10)]
                },
                "properties": {
                    "name": f"{lon}° lon"
                }
            })
            if lon != 0:  # Skip prime meridian label as an example
                label = f"<div style='color: blue; font-size: 10px; background-color: white;'>{lon}°</div>"
                icon = DivIcon(html=label)
                marker = Marker(location=(0, lon), icon=icon)
                markers.append(marker)

        grid_layer = GeoJSON(data=lines, style={"color": "blue", "weight": 1})

        return grid_layer, markers


    @staticmethod
    def plot_data_dic_on_map(
        data_dic: Dict[str, Dict[str, pd.DataFrame]],
        grid: bool = True,
        colors: Optional[List[str]] = None,
        labels: bool = True,
        latitude_column: str = 'latitude',
        longitude_column: str = 'longitude',
        map_title: str = "Map Title",
        polygons: Optional[List[Dict]] = None,
        fill_polygons: bool = True
    ) -> Map:
        """
        Plots a dictionary of data frames on a map with optional grid, labels, and polygons.

        Parameters:
        - data_dic (dict): Dictionary of data frames to plot, with keys as labels and values as dictionaries with 'data' key containing the data frame.
        - grid (bool): Whether to add a grid layer. Default is True.
        - colors (list): List of colors for the data layers. If None, colors are generated randomly. Default is None.
        - labels (bool): Whether to add labels to the data layers. Default is True.
        - latitude_column (str): Name of the latitude column. Default is 'latitude'.
        - longitude_column (str): Name of the longitude column. Default is 'longitude'.
        - map_title (str): Title of the map. Default is "Map Title".
        - polygons (list): List of dictionaries for polygons to add, each containing 'coordinates' and optional 'color'. Default is None.
        - fill_polygons (bool): Whether to fill the polygons. If False, only the borders are drawn. Default is True.

        Returns:
        - m (Map): The ipyleaflet Map object with the plotted data.
        """
        # Create the map
        m = Map(center=(15, 35), zoom=4)

        # Generate random colors if none are provided
        if colors is None:
            colors = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(len(data_dic))]

        # Add each DataFrame as a layer on the map
        for i, (label, data) in enumerate(data_dic.items()):
            df = data['data']
            gdf = map_display.df_to_gdf(df, lat_col=latitude_column, lon_col=longitude_column)
            geo_data = GeoData(
                geo_dataframe=gdf,
                style={
                    'color': colors[i % len(colors)],
                    'opacity': 0.5,
                    'weight': 1.9,
                    'dashArray': '2',
                    'fillOpacity': 0.6
                },
                hover_style={
                    'fillColor': 'red',
                    'fillOpacity': 0.2
                },
                point_style={
                    'radius': 0.1,
                    'color': 'red',
                    'fillOpacity': 0.8,
                    'fillColor': 'blue',
                    'weight': 1
                }
            )
            m.add_layer(geo_data)

            # Add label markers
            if labels:
                center_lat = df[latitude_column].mean()
                center_lon = df[longitude_column].mean()
                label_html = f"<div style='color: {colors[i % len(colors)]}; font-size: 12px; background-color: white;'>{label}</div>"
                icon = DivIcon(html=label_html)
                marker = Marker(location=(center_lat, center_lon), icon=icon)
                m.add_layer(marker)

        # Add grid layer if required
        if grid:
            grid_layer, grid_markers = map_display.create_grid_layer()
            m.add_layer(grid_layer)
            for marker in grid_markers:
                m.add_layer(marker)

        # Add polygons if provided
        if polygons:
            map_display.add_polygons_to_map(m, polygons, fill_polygons)

        # Add map title
        title_html = HTML(f"<h3 style='text-align: center; color: black;'>{map_title}</h3>")
        title_control = WidgetControl(widget=title_html, position='topright')
        m.add_control(title_control)

        # Adjust title position using CSS
        title_html.layout.margin = '10px 10px 10px 50%'
        title_html.layout.width = '400px'

        # Display the map
        return m

    @staticmethod
    def search_limits_to_polygon(search_limits: Dict[str, Dict[str, float]],color='black') -> List[Dict[str, any]]:
        """
        Creates a polygon from the given search limits.

        Parameters:
        - search_limits (dict): A dictionary containing 'longitude' and 'latitude' limits.
            Example:
            search_limits = {
                'longitude': {'min': 10, 'max': 20},
                'latitude': {'min': 30, 'max': 40},
                'time': {'min': '2024-06-01 00:16:10', 'max': '2024-06-01 00:16:10'} (optional)
            }

        Returns:
        - List[Dict]: A list containing a dictionary with polygon coordinates and color.
        """
        try:
            lon_min = search_limits['longitude']['min']
            lon_max = search_limits['longitude']['max']
            lat_min = search_limits['latitude']['min']
            lat_max = search_limits['latitude']['max']

            polygon = [
                {
                    'coordinates': [
                        [lat_min, lon_min],
                        [lat_min, lon_max],
                        [lat_max, lon_max],
                        [lat_max, lon_min],
                        [lat_min, lon_min]
                    ],
                    'color': color
                }
            ]
            
        except:
            polygon = [] 

        return polygon
    
    @staticmethod
    def search_limits_to_string(self,search_limits):
        """
        Generate a descriptive string based on the provided search limits dictionary.

        Parameters:
        - search_limits (dict): Dictionary containing search limits with 'min' and 'max' values for each key.
        example:
            search_limits = {
                'longitude':{'min':50,'max':60},
                'latitude':{'min':10,'max':20},
            }
        Returns:
        - str: A descriptive string summarizing the search limits.
        """
        parts = []
        for key, limits in search_limits.items():
            min_val = limits.get('min')
            max_val = limits.get('max')
            parts.append(f"{key.capitalize()}: {min_val} to {max_val}")
        return ', '.join(parts)

# from typing import List, Dict, Tuple

    @staticmethod
    def find_polygon_centroid(coordinates: List[List[float]]) -> Tuple[float, float]:
        """
        Finds the centroid of a polygon using shapely.

        Parameters:
        - coordinates (List[List[float]]): A list of [latitude, longitude] pairs representing the vertices of the polygon.

        Returns:
        - Tuple[float, float]: The (latitude, longitude) of the centroid.
        """
        # Ensure coordinates are in the correct format (List of Tuples)
        coords = [(lon, lat) for lat, lon in coordinates]
        polygon = ShapelyPolygon(coords)
        centroid = polygon.centroid
        return (centroid.y, centroid.x)
    
    @staticmethod
    def calculate_mean_centroid(polygons: List[Dict[str, List[List[float]]]]) -> Tuple[float, float]:
        """
        Calculates the mean overall centroid from a list of polygons.

        Parameters:
        - polygons (List[Dict[str, List[List[float]]]]): A list of polygons, each represented by a dictionary with a 'coordinates' key containing a list of [latitude, longitude] pairs.

        Returns:
        - Tuple[float, float]: The (latitude, longitude) of the mean overall centroid.
        """
        if not polygons:
            raise ValueError("The list of polygons is empty.")

        centroids = [map_display.find_polygon_centroid(polygon['coordinates']) for polygon in polygons]
        
        mean_lat = np.mean([lat for lat, lon in centroids])
        mean_lon = np.mean([lon for lat, lon in centroids])
        
        return (mean_lat, mean_lon)

    @staticmethod
    def add_coordinates_display(m):
        # Create a Label widget to show the coordinates
        coordinate_label = Label()

        # Function to update the label with the coordinates
        def handle_interaction(**kwargs):
            if kwargs.get('type') == 'mousemove':
                lat, lng = kwargs.get('coordinates')
                coordinate_label.value = f"Latitude: {lat:.4f}, Longitude: {lng:.4f}"

        # Attach the function to the map's interaction event
        m.on_interaction(handle_interaction)

        # Return a VBox containing the map and the coordinate label
        return VBox([m, coordinate_label])

    @staticmethod
    def set_english_labels(m):
        # Create a new tile layer with English labels
        english_tile_layer = TileLayer(
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            attribution="Map data © OpenStreetMap contributors"
        )

        # Remove existing layers (if necessary) and add the English tile layer
        m.clear_layers()
        m.add_layer(english_tile_layer)

        return m
    @staticmethod
    def add_marker(m, marker):
        # Extract information from the dictionary, with default values for color and label
        location = marker.get('location')
        color = marker.get('color', 'blue')
        label_text = marker.get('label', '')

        # Define the HTML for the DivIcon, with improved styling
        icon_html = f"""
        <div style="display: flex; align-items: center; font-family: Arial, sans-serif;">
            <div style="background-color: {color}; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 3px transparent;"></div>
            # <span style="font-size: 14px; font-weight: bold; color: black; background-color: transparent; padding: 3px 6px; border-radius: 4px; box-shadow: 0 0 2px transparent;">
            #     {label_text}

            </span>
        </div>
        """

        # Create a DivIcon with the custom HTML
        icon = DivIcon(html=icon_html, icon_size=(150, 36), icon_anchor=(0, 0))

        # Create the marker at the specified location with the custom icon
        marker = Marker(location=location, icon=icon)

        # Add the marker to the map
        m.add_layer(marker)

        return m


    

    @staticmethod
    def convert_dms_to_location(input):
        """
        Convert coordinates from either DMS string format or tuple format to decimal degrees.

        Parameters:
        -----------
        input : str or tuple
            The input coordinate in either DMS string format or tuple format.

        Returns:
        --------
        tuple
            A tuple containing latitude and longitude in decimal degrees format.
        """
        def dms_to_decimal(degrees, minutes, seconds, direction):
            """
            Convert coordinates from Degrees, Minutes, Seconds (DMS) format to Decimal Degrees.
            
            Parameters:
            -----------
            degrees : int
                The degree part of the coordinate.
            minutes : int
                The minute part of the coordinate.
            seconds : int
                The second part of the coordinate.
            direction : str
                The direction of the coordinate ('N', 'S', 'E', 'W').
            
            Returns:
            --------
            float
                The coordinate in decimal degrees.
            """
            decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
            if direction in ['S', 'W']:
                decimal_degrees *= -1
            return decimal_degrees

        def parse_dms_string(dms_string):
            """
            Parse a coordinate string in the format "33°49′15″N 35°29′18″E" and convert to decimal degrees.

            Parameters:
            -----------
            dms_string : str
                The coordinate string in DMS format.

            Returns:
            --------
            tuple
                A tuple containing latitude and longitude in decimal degrees format.
            """
            pattern = re.compile(r"(\d+)°(\d+)′(\d+)″([NS]) (\d+)°(\d+)′(\d+)″([EW])")
            match = pattern.match(dms_string)
            
            if not match:
                raise ValueError("Invalid coordinate string format")

            # Extract values from the matched groups
            lat_degrees, lat_minutes, lat_seconds, lat_direction, lon_degrees, lon_minutes, lon_seconds, lon_direction = match.groups()

            # Convert to decimal degrees
            latitude = dms_to_decimal(int(lat_degrees), int(lat_minutes), int(lat_seconds), lat_direction)
            longitude = dms_to_decimal(int(lon_degrees), int(lon_minutes), int(lon_seconds), lon_direction)

            return (latitude, longitude)
        
        if isinstance(input, str):
            # Handle DMS string format
            return parse_dms_string(input)
        elif isinstance(input, tuple):
            # Handle tuple format
            if len(input) != 2 or not all(isinstance(i, tuple) and len(i) == 4 for i in input):
                raise ValueError("Invalid tuple format")
            lat_dms, lon_dms = input
            latitude = dms_to_decimal(*lat_dms)
            longitude = dms_to_decimal(*lon_dms)
            return (latitude, longitude)
        else:
            raise ValueError("Invalid input format")

# # Example usage:
# dms_string = "33°49′15″N 35°29′18″E"
# tuple_format = ((33, 49, 15, 'N'), (35, 29, 18, 'E'))

# print(convert_dms_to_location(dms_string))  # Output: (33.82083333333333, 35.48833333333333)
# print(convert_dms_to_location(tuple_format))  # Output: (33.82083333333333, 35.48833333333333)



# The string containing the coordinate limits
    @staticmethod
    def coordinate_limits2filter_dic(coordinate_limits):
        # Split the string to get individual coordinate pairs
        coords = coordinate_limits.split(':')

        # Extract latitude and longitude from each part using geopy
        point1 = geopy.Point(coords[0].strip())
        point2 = geopy.Point(coords[1].strip())

        # Extract the latitudes and longitudes
        lat1, lon1 = point1.latitude, point1.longitude
        lat2, lon2 = point2.latitude, point2.longitude

        # Determine the min and max for latitude and longitude
        lat_min, lat_max = sorted([lat1, lat2])
        lon_min, lon_max = sorted([lon1, lon2])

        # Create the filter dictionary
        filter_dict = {
            'longitude': ('between', (lon_min, lon_max)),
            'latitude': ('between', (lat_min, lat_max))
        }
        return filter_dict

