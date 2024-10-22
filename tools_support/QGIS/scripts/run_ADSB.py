import os
import pickle
import sys
from qgis.core import QgsProject
import pandas as pd

import sys
from pathlib import Path
import os
# current_path = Path(os.getcwd())
# sys.path.append(str(Path (current_path.parents[2] / "common" / "python_aux")))  # Ensure the path is a string


# print (sys.path)


# import file_aux as filea
# sys.path.append('..')  # Add the parent directory to sys.path

#from QGISDriver import QGIS

RestartProject()

layer_name = 'flights'
data_file = r"C:\work\tools\QGIS\data\ADSB\vessels_data.csv"


csv_file_name = "aircraft_data_20241007_142123.csv"
# csv_file_name = "aircraft_data_20241008_125040.csv"

out_folder_name = csv_file_name.split('.')[0]
out_folder_name = rf"./pkl/{out_folder_name}"
out_folder_name = rf"C:\work\code\algo-dayrun\src\test\spoofing_algo\pkl\aircraft_data_20241007_142123"


run_name = 'new'





vessels_data_file=fr"{out_folder_name}\vessels_data_{run_name}.csv"
CreateVesselPathLayer(f"vessels_data_{run_name}",vessels_data_file,classification_node='name',location_columns_dic={'lat': 'lat', 'lon': 'lon'})    

layer_name = 'flights_spoof'
# events_file_name = file_name=fr"{out_folder_name}\events_data_{run_name}.csv"
# events_df = pd.read_csv(events_file_name)
# with open(r"C:\work\tools\QGIS\data\ADSB\vessels_events_clusters.pkl", 'rb') as file:
#      events_clusters = pickle.load(file)

events_data_file = f"{out_folder_name}\events_data_{run_name}.csv"
print(events_data_file)
# CreateSpoofLayersAndClusters(events_df, events_clusters, layer_name)
# CreateSpoofLayers(f'spoof_{run_name}',rf"C:\work\tools\QGIS\data\ADSB\vessels_events_{run_name}.csv",highlight_clusters=None)
CreateSpoofLayers(f'events_data_{run_name}',events_data_file,highlight_clusters=None)
