import os
import pickle
from qgis.core import QgsProject


restart_project()

# Set your parameters
pkl_directory = r"C:\work\tools\QGIS\data"  # Path to the directory containing the pickle files
layer_name = "SpoofEvents"  # Name for the QGIS layers

# Construct file paths for the pickle files
db_name = '2023110107.db'
db_name = '20240401.db'

db_name_clean = db_name.split('.')[0]

events_df_file = os.path.join(pkl_directory, f'events_df_{db_name}.pkl')
events_clusters_file = os.path.join(pkl_directory, f'events_clusters_{db_name}.pkl')

# Load the DataFrames from pickle files
with open(events_df_file, 'rb') as df_file:
    events_df = pickle.load(df_file)

with open(events_clusters_file, 'rb') as clusters_file:
    events_clusters = pickle.load(clusters_file)

# Check if the loaded data is valid
if events_df is None or events_clusters is None:
    print("Error: Unable to load events data from pickle files.")
else:
    # Run the create_spoof_layer function
    # create_spoof_layers(events_df, events_clusters, layer_name)

# Example usage
    csv_file = r"C:\work\data\ships\20240401\events.csv"
    layer_name = 'spoof_layer1'
    output_shapefile = None  # Optional, set None to avoid saving to shapefile
    # create_spoof_layer_mod(events_df,layer_name)

    create_spoof_layers(events_df,events_clusters,layer_name,show_none_clustered_events=False)
    # create_spoof_layer(csv_file, 'kuku', output_shapefile=None)
                       

layer_name = 'ships'
data_file = f"C:\work\data\ships//{db_name_clean}/ships_data.csv"

CreateVesselPathLayer(layer_name,data_file,classification_node='name')
ChangeTimeZone(layer_name, time_zone='UTC', column_names='time')
