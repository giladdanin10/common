import json

import sys
from pathlib import Path
import os
current_path = Path(os.getcwd())
sys.path.append(str(Path (current_path.parents[1] / 'python_aux')))
from parse_aux import *
import os
import re
import html


from datetime import datetime
import xml.etree.ElementTree as ET



class QGIS_Utils:
    def __init__(self):
        pass


    @staticmethod
    def create_bounding_box(filter_dic=None,out_file=None,min_lon=None, min_lat=None, max_lon=None, max_lat=None,CRF='EPSG:4326'):
        params_dict = locals()
        check_none_keys(params_dict,['out_file'])

        if (filter_dic is not None):
            min_lon = filter_dic['longitude'][1][0]
            max_lon = filter_dic['longitude'][1][1]
            min_lat = filter_dic['latitude'][1][0]
            max_lat = filter_dic['latitude'][1][1]

        

        # Create the GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:4326"
                }
            },
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [min_lon, min_lat],  # Bottom-left corner
                                [max_lon, min_lat],  # Bottom-right corner
                                [max_lon, max_lat],  # Top-right corner
                                [min_lon, max_lat],  # Top-left corner
                                [min_lon, min_lat]   # Closing the polygon back to the bottom-left corner
                            ]
                        ]
                    },
                    "properties": {
                        "name": f"BoundingBox {CRF}"
                    }
                }
            ]
        }

        # Write the GeoJSON to a file
        with open(out_file, "w") as f:
            json.dump(geojson, f, indent=4)

        print("GeoJSON file created: bounding_box_epsg4326.geojson")




    @staticmethod
    def filter_dic2query_filter_file(filter_dic, output_file):
        """
        Creates a valid XML query filter file from a filter dictionary for QGIS.

        :param filter_dic: Dictionary containing filter conditions.
                            Supported operators: '==', '!=', '<', '<=', '>', '>=', 'between'.
        :param output_file: Output file name where the filter will be saved. If the directory does not exist, it will be created.
        """
        # Ensure the directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Helper function to format the datetime values as ISO 8601 with milliseconds
        def format_datetime_for_qgis(dt):
            if isinstance(dt, str):
                try:
                    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.000')
                except ValueError:
                    return dt  # If already in the right format
            return dt

        # Construct the filter query
        filter_queries = []

        for column, conditions in filter_dic.items():
            if isinstance(conditions, tuple):
                operator, value = conditions

                # Handle "between" case
                if operator == 'between' and isinstance(value, tuple) and len(value) == 2:
                    lower_bound, upper_bound = value
                    lower_bound = format_datetime_for_qgis(lower_bound)
                    upper_bound = format_datetime_for_qgis(upper_bound)
                    filter_query = f'"{column}" >= \'{lower_bound}\' AND "{column}" <= \'{upper_bound}\''
                else:
                    formatted_value = format_datetime_for_qgis(value)
                    filter_query = f'"{column}" {operator} \'{formatted_value}\''
                filter_queries.append(filter_query)

            elif isinstance(conditions, list):  # Handle multiple conditions
                for condition in conditions:
                    operator, value = condition
                    formatted_value = format_datetime_for_qgis(value)
                    filter_query = f'"{column}" {operator} \'{formatted_value}\''
                    filter_queries.append(filter_query)

        # Join all conditions with AND
        query_string = " AND ".join(filter_queries)

        # Create the XML structure
        root = ET.Element('Query')
        root.text = query_string if query_string else None

        # Write the XML to the output file
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"Filter file created: {output_file}")


