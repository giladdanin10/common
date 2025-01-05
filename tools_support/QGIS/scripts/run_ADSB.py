import os
import pickle
import sys
from qgis.core import QgsProject
import pandas as pd

import sys
from pathlib import Path
import os
runn_dir_base = r'C:\work\code\TipAndQue-algo\src\test\spoofing\run_results\\'
run_name = 'aircraft_data_20240401_algo_dr_based'   
in_dir = runn_dir_base +run_name+'\\'+ "QGIS_in" + "\\"

#in_dir = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'

events_data_file = in_dir+"spoof_cases_df.csv"
vessels_data_file = in_dir+"vessels_data.csv"
CreateSpoofLayers(run_name,events_data_file,highlight_clusters=None)
CreateVesselPathLayer(run_name,vessels_data_file,classification_node='vessel_id',location_columns_dic={'lat': 'lat', 'lon': 'lon'})    
