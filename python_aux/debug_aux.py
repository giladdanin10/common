import pandas as pd
import numpy as np
import dict_aux as dicta
import convert_aux as converta

def CompareDfs(df1, df2, to_print=True, ID_columns=None, mode='check_existence', compare_columns=None, eps=1e-5, ignore_time_columns=False,ignore_columns=None,report_file_name='compare_res.txt'):    
    """
    Compares two DataFrames based solely on the existence of values in specific ID columns
    and returns IDs that are unique to each DataFrame.

    Parameters: 
        df1 (pd.DataFrame): The first DataFrame.
        df2 (pd.DataFrame): The second DataFrame.
        to_print (bool): If True, prints the unique IDs or equality message.
        ID_columns (list): List of column names to use as the ID for comparison.
        eps (float): The tolerance level for comparing numeric columns.

    Returns:
        dict: A dictionary with two lists:
              'only_in_df1' - List of unique IDs in df1 but not in df2.
              'only_in_df2' - List of unique IDs in df2 but not in df1.
    """

    diff_dic = {}
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)


    if ID_columns is None:
        df1['row_num'] = df1.index
        df2['row_num'] = df2.index
        ID_columns = 'row_num'
        mode = 'check_values'

    # Ensure ID_columns is a list
    if not isinstance(ID_columns, list):
        ID_columns = [ID_columns]


    if df1 is None:
        df1 = pd.DataFrame()

    if df2 is None:
        df2 = pd.DataFrame()

    if df1.empty:
        if (df2.empty):
            diff_dic = {}
            print('DataFrames are equal')
        else:
            diff_dic['only_in_df2'] = df2[ID_columns].agg('-'.join, axis=1).tolist()
        return diff_dic
    
    if df2.empty:
        if (df1.empty):
            diff_dic = {}
            print('DataFrames are equal')
        else:
            diff_dic['only_in_df1'] = df1[ID_columns].agg('-'.join, axis=1).tolist()
        return diff_dic

    # Create unique ID columns by joining the ID columns
    df1['unique_id'] = df1[ID_columns].astype(str).agg('-'.join, axis=1)
    df2['unique_id'] = df2[ID_columns].astype(str).agg('-'.join, axis=1)
    
    # Find unique IDs in each DataFrame
    ids_only_in_df1 = df1[~df1['unique_id'].isin(df2['unique_id'])]['unique_id'].tolist()
    ids_only_in_df2 = df2[~df2['unique_id'].isin(df1['unique_id'])]['unique_id'].tolist()

    if len(ids_only_in_df1) > 0:
        diff_dic['only_in_df1'] = ids_only_in_df1

    if len(ids_only_in_df2) > 0:
        diff_dic['only_in_df2'] = ids_only_in_df2

    if mode == 'check_existence':
        return diff_dic

    elif mode == 'check_values':
        # Remove rows with unique IDs that are only in one of the DataFrames
        df1 = df1[~df1['unique_id'].isin(ids_only_in_df1)]
        df2 = df2[~df2['unique_id'].isin(ids_only_in_df2)]
        df1.sort_values(by='unique_id', inplace=True)
        df1.reset_index(drop=False, inplace=True)
        df2.sort_values(by='unique_id', inplace=True)
        df2.reset_index(drop=False, inplace=True)
        
        if compare_columns is None:
            compare_columns = df1.columns.tolist()

        compare_columns = converta.VarToList(compare_columns)    
        # Remove ID columns from the list of columns to compare
        for column in ID_columns:
            if column in compare_columns:
                compare_columns.remove(column)
            
        if (ignore_columns is not None) and (len(ignore_columns) > 0):
            for column in ignore_columns:
                if column in compare_columns:
                    compare_columns.remove(column)

        for column in compare_columns:
            if ignore_time_columns:
                if ('time' in column) or ('date' in column):
                    continue
            
            # Check if the column is numeric
            if pd.api.types.is_numeric_dtype(df1[column]) and not pd.api.types.is_bool_dtype(df1[column]):
                # Calculate mean of the values in both columns
                mean_value = np.mean([df1[column].mean(), df2[column].mean()])

                # Calculate the absolute difference
                diff = np.abs(df1[column] - df2[column])

                # Normalize by the mean value
                normalized_diff = diff / mean_value

                # Identify indices where the normalized difference exceeds the epsilon
                ind_diff = normalized_diff > eps
            else:
                try:
                    # For non-numeric (including boolean) columns, use direct comparison
                    ind_diff = df1[column] != df2[column]
                except Exception as e:
                    print(f"Error comparing column '{column}': {e}")
                    ind_diff = pd.Series([False] * len(df1))

            if ind_diff.any():  # Check if ind_diff is not empty
                diff_dic[column] = {}
                diff_dic[column]['df1_index'] = df1.loc[ind_diff, 'index'].tolist()  # Optionally convert to a list for easier readability
                diff_dic[column]['df2_index'] = df2.loc[ind_diff, 'index'].tolist()  # Optionally convert to a list for easier readability                                 
                for id_column in ID_columns:
                    diff_dic[column][id_column] = df1.loc[ind_diff, id_column].tolist()
                # diff_dic[column][ID_columns] = df1.loc[ind_diff, ID_columns].astype(str).agg('-'.join, axis=1).tolist()
                # diff_dic[column]['unique_id'] = df1.loc[ind_diff, 'unique_id'].tolist()

                diff_dic[column]['df1'] = df1.loc[ind_diff, column].tolist()
                diff_dic[column]['df2'] = df2.loc[ind_diff, column].tolist()

    if not diff_dic:
        print('DataFrames are equal')
    else:
        print('DataFrames are different; see diff_dic for details')

    
    with open(report_file_name, 'w') as f:
        if ('only_in_df1' in diff_dic):
            f.write(f'{ID_columns[0]}\'s only in df1:\n')
            for i,id_val in enumerate(diff_dic['only_in_df1']):
                f.write(f'{id_val}\n')
            f.write('\n')
        
        if ('only_in_df2' in diff_dic):
            f.write(f'{ID_columns[0]}\'s only in df1:\n')
            for i,id_val in enumerate(diff_dic['only_in_df2']):
                f.write(f'{id_val}\n')
            f.write('\n')



        for key in compare_columns:
            if (key in diff_dic.keys()):
                f.write(f'comparing "{key}" values:\n')
                for i,id_val in enumerate(diff_dic[key][ID_columns[0]]):
                    f.write(f'{id_val}: df1 - {diff_dic[key]['df1'][i]}, df2 - {diff_dic[key]['df2'][i]} \n')
                f.write('\n')




    return diff_dic