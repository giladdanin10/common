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

run_dir_base = r'C:\\work\\run_results'
date = '20250201'
# run_name = "20240901_spoofing_hop_N_std_th_1"   
# run_names = ["20240901_spoofing_full","20240901_spoofing_full_check_events"]   


# run_names = ["20240901_spoofing_full_debug_clusters"]   
run_names = ["20250201_spoofing_full"]   
# run_names = ["20250201_spoofing_full_debug"]   
# run_names = ["20250201_spoofing_full_debug_single_vessel_event_en"]
# run_names = ['20250201_spoofing_full - 11_20 before big run']  

# run_dir_base = r'C:\work\code\TipAndQue-algo-spoofing\src\test\run_results\\'
# run_names = ['20250201_spoofing_full']
for run_name in run_names:
    #in_dir = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'
    run_dir = f"{run_dir_base}\\{date}\\{run_name}"
    print(os.path.exists(run_dir_base))
    vessels_data_file = f"{run_dir}\\QGIS_in\\vessels_data.csv"
    # CreateSpoofLayers(layer_name = run_name,run_dir = run_dir_base+run_name,highlight_events=None)
    file_name_prefix = run_name.split("_")[0]+"_0915_0930_"
    file_name_prefix = ""
# 2024901_2330_2345_spoof_cases_df

    spoof_cases_df_file=rf'{run_dir}\\spoof_cases_df\\{file_name_prefix}spoof_cases_df.csv'
    spoof_events_gdf_file=rf'{run_dir}\\spoof_events_gdf\\{file_name_prefix}spoof_events_gdf.csv'

    
    layer_types=['entry_points','exit_points','drift_points','entry_exit_drift_lines','drift_areas']
    # layer_types=['drift_points'] 


    CreateSpoofLayers(layer_name = run_name,
                        spoof_cases_df_file=spoof_cases_df_file,
                        spoof_events_gdf_file=spoof_events_gdf_file,
                        highlight_events=None,exclude_events=None
                        ,file_name_prefix=file_name_prefix,iteration_num=None,
                        layer_types=layer_types,
                        drift_point_size=10)





# CreateVesselPathLayer(run_name+'_vessels_data',vessels_data_file,classification_node='vessel_id',location_columns_dic={'lat': 'lat', 'lon': 'lon'})    

# app

# run_dir_base = r'C:\work\code\TipAndQue-algo\src\test\pipline\spoof\testing\temp_output\\'
# in_dir = run_dir_base + "QGIS_in" + "\\"
# CreateSpoofLayers('app',events_data_file,highlight_events=-1)


#CreateSpoofeventLayer(run_dir_base+run_name,events_data_file,highlight_events=None)
