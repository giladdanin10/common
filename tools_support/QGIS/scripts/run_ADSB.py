import os
import pickle
import sys
from qgis.core import QgsProject
import pandas as pd
# sys.path.append('..')  # Add the parent directory to sys.path

#from QGISDriver import QGIS

RestartProject()

layer_name = 'flights'
data_file = r"C:\work\tools\QGIS\data\ADSB\vessels_data.csv"
run_name = 'base'


CreateVesselPathLayer(layer_name,data_file,classification_node='name',location_columns_dic={'lat': 'lat', 'lon': 'lon'})    

layer_name = 'flights_spoof'
events_file_name = r"C:\work\tools\QGIS\data\ADSB\vessels_events.csv"
events_df = pd.read_csv(events_file_name)
with open(r"C:\work\tools\QGIS\data\ADSB\vessels_events_clusters.pkl", 'rb') as file:
     events_clusters = pickle.load(file)

# CreateSpoofLayersAndClusters(events_df, events_clusters, layer_name)
CreateSpoofLayers(f'spoof_{run_name}',rf"C:\work\tools\QGIS\data\ADSB\vessels_events_{run_name}.csv",highlight_clusters=None)
