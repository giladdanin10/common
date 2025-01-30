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
run_name = "20240901_spoofing"   

#in_dir = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'

events_data_file = run_dir_base+run_name+"\\spoof_cases_df\\"+"spoof_cases_df.csv"
vessels_data_file = run_dir_base+run_name+"\\vessels_data\\vessels_data.csv"
# CreateSpoofLayers(layer_name = run_name,run_dir = run_dir_base+run_name,highlight_clusters=None)
file_name_prefix = run_name.split("_")[0]+"_1000_1015_"
file_name_prefix = ""

spoof_cases_df_csv_file=run_dir_base+run_name+'\\spoof_cases_df\\spoof_cases_df.csv'
spoof_clusters_gdf_csv_file=run_dir_base+run_name+'\\spoof_clusters_gdf\\spoof_clusters_gdf.csv'
# spoof_cases_df_csv_file = "C:\\work\\code\\TipAndQue-algo\src\\test\\spoofing\\spoof_cases_df.csv"
# spoof_clusters_gdf_csv_file ="C:\\work\\code\\TipAndQue-algo\\src\\test\\run_results\\20240901_spoofing_full\\spoof_clusters_gdf\\20240901_1030_1045_spoof_clusters_gdf.csv"
# spoof_clusters_gdf_csv_file = "C:\\work\\code\\TipAndQue-algo\\src\\test\\run_results\\20240901_spoofing\\spoof_clusters_gdf\\spoof_clusters_gdf.csv"
#spoof_clusters_gdf_csv_file = "C:\\work\\code\\TipAndQue-algo\\src\\test\\run_results\\20240901_spoofing_full\\spoof_clusters_gdf\\spoof_clusters_gdf_temp.csv"

# spoof_clusters_gdf_csv_file = None

CreateSpoofLayers(layer_name = run_name,
                    spoof_cases_df_csv_file=spoof_cases_df_csv_file,
                    spoof_clusters_gdf_csv_file=spoof_clusters_gdf_csv_file,
                    highlight_clusters=None,exclude_clusters=None,file_name_prefix=file_name_prefix,iteration_num=None)

CreateVesselPathLayer(run_name,vessels_data_file,classification_node='vessel_id',location_columns_dic={'lat': 'lat', 'lon': 'lon'})    

# app

# run_dir_base = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'
# in_dir = run_dir_base + "QGIS_in" + "\\"
# CreateSpoofLayers('app',events_data_file,highlight_clusters=-1)


#CreateSpoofClusterLayer(run_dir_base+run_name,events_data_file,highlight_clusters=None)
