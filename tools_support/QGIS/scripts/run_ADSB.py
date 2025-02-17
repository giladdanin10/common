import os
import pickle
import sys
from qgis.core import QgsProject
import pandas as pd

import sys
from pathlib import Path
import os
# algo

RestartProject()

run_dir_base = r'C:\work\code\TipAndQue-algo\src\test\run_results\\'
# run_name = "20240901_spoofing_hop_N_std_th_1"   
run_names = ["20240901_spoofing_full","20240901_spoofing_full_check_clusters"]   

run_names = ["20240901_spoofing_alina","20240901_spoofing_full"]   
  

for run_name in run_names:
    #in_dir = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'

    vessels_data_file = run_dir_base+run_name+"\\QGIS_in\\vessels_data.csv"
    # CreateSpoofLayers(layer_name = run_name,run_dir = run_dir_base+run_name,highlight_clusters=None)
    file_name_prefix = run_name.split("_")[0]+"_2330_2345_"
    # file_name_prefix = ""
# 2024901_2330_2345_spoof_cases_df

    spoof_cases_df_file=run_dir_base+run_name+f'\\spoof_cases_df\\{file_name_prefix}spoof_cases_df.csv'
    spoof_clusters_gdf_file=run_dir_base+run_name+f'\\spoof_clusters_gdf\\{file_name_prefix}spoof_clusters_gdf.csv'


    layer_types=['entry_points','exit_points','drift_points','entry_exit_drift_lines','drift_areas']
    layer_types=['drift_points'] 


    CreateSpoofLayers(layer_name = run_name,
                        spoof_cases_df_file=spoof_cases_df_file,
                        spoof_clusters_gdf_file=spoof_clusters_gdf_file,
                        highlight_clusters=None,exclude_clusters=None
                        ,file_name_prefix=file_name_prefix,iteration_num=None,
                        layer_types=layer_types)


# run_name = "20240901_spoofing"   
# spoof_cases_df_file=run_dir_base+run_name+'\\spoof_cases_df\\spoof_cases_df_mod.csv'
# spoof_clusters_gdf_file=run_dir_base+run_name+'\\spoof_clusters_gdf\\spoof_clusters_gdf_mod.csv'
# spoof_cases_df_file=run_dir_base+run_name+'\\spoof_cases_df\\spoof_cases_df.csv'
# spoof_clusters_gdf_file=run_dir_base+run_name+'\\spoof_clusters_gdf\\spoof_clusters_gdf.csv'


# CreateSpoofLayers(layer_name = run_name+"_mod",
#                     spoof_cases_df_file=spoof_cases_df_file,
#                     spoof_clusters_gdf_file=spoof_clusters_gdf_file,
#                     highlight_clusters=None,exclude_clusters=None,file_name_prefix=file_name_prefix,iteration_num=None)



CreateVesselPathLayer(run_name+'_vessels_data',vessels_data_file,classification_node='vessel_id',location_columns_dic={'lat': 'lat', 'lon': 'lon'})    

# app

# run_dir_base = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'
# in_dir = run_dir_base + "QGIS_in" + "\\"
# CreateSpoofLayers('app',events_data_file,highlight_clusters=-1)


#CreateSpoofClusterLayer(run_dir_base+run_name,events_data_file,highlight_clusters=None)
