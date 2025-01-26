import h3 
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon


# Load geographic data from a file get list of hexagons cell by resolution by geopandas dataframe


def load_geodata(file_path: str) -> gpd.GeoDataFrame:
    """
    Read either a shapefile (.shp) or GeoJSON file and return a GeoDataFrame.
    
    Parameters:
        file_path (str): Path to the geographic file (.shp or .geojson)
    
    Returns:
        gpd.GeoDataFrame: The loaded geographic data
        
    Raises:
        ValueError: If file extension is not supported
        FileNotFoundError: If file does not exist
    """
    # Convert to Path object for easier handling
    
    path = Path(file_path)
     

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    file_extension = path.suffix.lower()
    
    try:
        if file_extension == '.shp':
            return gpd.read_file(file_path)
        elif file_extension == '.geojson':
            return gpd.read_file(file_path, driver='GeoJSON')
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}. Use .shp or .geojson")
            
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


# get list of hexagons cell by resolution by geopandas dataframe



def get_hexagons_list(geo_data: gpd.GeoDataFrame, resolution: int) -> list:
    """
    Get a list of hexagons at a given resolution that cover the bounding box of the GeoDataFrame.
    
    Parameters:
        geo_data (gpd.GeoDataFrame): The geographic data
        resolution (int): The resolution of the hexagons (0-15)
    
    Returns:
        list: List of H3 hexagon indices covering the area
        
    Raises:
        ValueError: If the GeoDataFrame is empty or resolution is invalid
    """
    # Check if GeoDataFrame is empty
    if geo_data.empty:
        raise ValueError("GeoDataFrame is empty")
        
    # Validate resolution
    if not 0 <= resolution <= 15:
        raise ValueError("Resolution must be between 0 and 15")
    
    # Ensure the GeoDataFrame is in WGS84 (EPSG:4326)
    if geo_data.crs is None:
        raise ValueError("GeoDataFrame must have a CRS defined")
    if geo_data.crs.to_epsg() != 4326:
        geo_data = geo_data.to_crs(epsg=4326)
    
    # Get the bounding box
    bounds = geo_data.total_bounds
    min_lng, min_lat, max_lng, max_lat = bounds
    # Create a bounding box polygon for H3
    bbox_coords = [
        [min_lat, min_lng],
        [min_lat, max_lng],
        [max_lat, max_lng],
        [max_lat, min_lng],
        [min_lat, min_lng]  # Close the polygon
    ]
    
    # Convert to H3 LatLngPoly
    h3shape = h3.LatLngPoly(bbox_coords)
    
    # Get hexagons using h3shape_to_cells (alias polygon_to_cells)
    hexagons = h3.h3shape_to_cells(h3shape, resolution)
    
    return list(hexagons)

pathfile= "/Users/nadavirshai/Documents/Tipandcue/qgis/test1.shp"
resolution=11
try:
        geodata_file = load_geodata(pathfile)
        print("geodata_file loaded ->  successfully!!!")
        
        print(f"list  hexagons: {get_hexagons_list(geodata_file, resolution)}")

except Exception as e:
        print(f"Error: {str(e)}") 
