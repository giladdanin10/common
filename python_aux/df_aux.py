
import sys
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import copy
import convert_aux as converta

algo_path = Path(r'C:\work\code\AIS-R-D\algo')
sys.path.append(str(algo_path))

# # Get the current working directory
# current_dir = Path.cwd()

# # Define the relative path
# algo_path = current_dir / 'code' / 'AIS-R-D' / 'algo'

# # Add the path to sys.path
# sys.path.append(str(algo_path))



import numpy as np
import pandas as pd
from convert_aux import * 
import convert_aux as CONVERT
from time_aux import *
from parse_aux import *
from str_aux import *
import list_aux as lista        


def merge_dataframes_on_index(df1, df2, how='left', mode='merge'):
    # Ensure that indices are aligned for merging
    df1 = df1.copy()
    df2 = df2.copy()

    # Merge DataFrames
    merged_df = df1.merge(df2, left_index=True, right_index=True, how=how, suffixes=('', '_dup'))

    if mode == 'merge':
        # Remove duplicate columns by merging the data
        cols = merged_df.columns
        for col in cols:
            if '_dup' in col:
                original_col = col.replace('_dup', '')
                if original_col in merged_df.columns:
                    # Handle duplication by backfilling with data from the duplicate column
                    merged_df[original_col] = merged_df[[original_col, col]].bfill(axis=1).iloc[:, 0]
                    merged_df.drop(columns=[col], inplace=True)
    elif mode == 'replace':
        # Replace data in mutual columns with data from df2
        cols = merged_df.columns
        for col in cols:
            if '_dup' in col:
                original_col = col.replace('_dup', '')
                if original_col in merged_df.columns:
                    # Replace data in original column with data from the duplicate column
                    merged_df[original_col] = merged_df[col]
                    merged_df.drop(columns=[col], inplace=True)

    return merged_df

def PrepareFilter(filter_dic):
    if isinstance(filter_dic, dict):
        # Recursively handle dictionaries
        return {key: PrepareFilter(value) for key, value in filter_dic.items()}
    elif isinstance(filter_dic, list):
        # Convert lists to tuples
        return tuple(PrepareFilter(item) for item in filter_dic)
    else:
        # Return other types as-is
        return filter_dic


def filter_df(df, filter_dic,to_copy=False):
    """
    Filters a DataFrame based on a dictionary of column filters.

    Parameters:
    df (pd.DataFrame): The DataFrame to be filtered.
    filter_dic (dict): A dictionary where keys are column names and values are either:
                       - A tuple with an operator and a value (for a single condition)
                       - A list of tuples for multiple conditions on the same column.

                       Supported operators: '==', '!=', '<', '<=', '>', '>=', 'between', 'str_filter'.

    Returns:
    pd.DataFrame: The filtered DataFrame or an empty DataFrame if any column does not exist.
    """

    if (filter_dic==None) or (len(filter_dic.keys())==0) or df is None or df.empty:
        return df
    
    
# convert layer definition from list to tupple ({'cluster_id': ['==', 1]} --> {'cluster_id': ('==', 1)})
    filter_dic = PrepareFilter(filter_dic)
    if (to_copy):
        filtered_df = copy.deepcopy(df)  # Create a copy of the DataFrame to avoid modifying the original
    else:
        filtered_df = df

    for column, conditions in filter_dic.items():

        if column not in filtered_df.columns:
            print(f"Error: Column '{column}' does not exist in the DataFrame. Existing columns: {list(filtered_df.columns)}")
            return pd.DataFrame()  # Return an empty DataFrame

        if not isinstance(conditions, list):
            conditions = [conditions]  # Convert to list if it's not already

        for condition in conditions:
            operator, value = condition

            if 'time' in column:  
                value = datetime2datenum(value) 



            if operator == '==':
                value = CONVERT.VarToList(value)
                if not isinstance(value, list):
                    value = [value]
                    
                # filtered_df = filtered_df[filtered_df[column].isin(value)]
                
                # filtered_df[column] = pd.Categorical(filtered_df[column], categories=value, ordered=True)

                # # Sort by column to enforce the order
                # filtered_df = filtered_df.sort_values(column)

                # Step 1: Filter the DataFrame by the name list
                filtered_df = filtered_df.loc[filtered_df[column].isin(value)].copy()  # Use .loc and .copy() to avoid the warning

                # Step 2: Preserve the order of the name list using pd.Categorical
                filtered_df[column] = pd.Categorical(filtered_df[column], categories=value, ordered=True)

                # Step 3: Sort the DataFrame by the order of the name list
                filtered_df = filtered_df.sort_values(by=column)
                

            elif operator == '!=':
                if isinstance(value, list):
                    filtered_df =  filtered_df[~filtered_df[column].isin(value)]
                else:
                    filtered_df =  filtered_df[filtered_df[column] != value]
            elif operator == '<':
                filtered_df =  filtered_df[filtered_df[column] < value]
            elif operator == '<=':
                filtered_df =  filtered_df[filtered_df[column] <= value]
            elif operator == '>':
                filtered_df =  filtered_df[filtered_df[column] > value]
            elif operator == '>=':
                filtered_df =  filtered_df[filtered_df[column] >= value]
            elif operator == 'between':
                if isinstance(value, tuple) and len(value) == 2:
                    lower_bound, upper_bound = value
                    filtered_df =  filtered_df[(filtered_df[column] >= lower_bound) & (filtered_df[column] <= upper_bound)]
                    if lower_bound > upper_bound:
                        print(f'Lower bound ({lower_bound}) is higher than upper bound ({upper_bound})')
                else:
                    raise ValueError(f"Value for 'between' must be a tuple of two elements: {value}")
            elif operator == 'str_filter':
                if filtered_df[column].dtype == 'object':  # Ensure it's a string column
                    filtered_values = filter_strs(filtered_df[column].tolist(), value)
                    filtered_df =  filtered_df[filtered_df[column].isin(filtered_values)]
                else:
                    raise ValueError(f"Column '{column}' is not of string type.")
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        
    return filtered_df



def repeat_single_value_in_column (df,value,column_name,to_print=False):
    if not isinstance(value, list) and not isinstance(value, np.ndarray):
        value = [value]

    # print(value)        
    if (len(value) != 1):
        if (to_print):
            print(f'value is not unique:{value}')
        return pd.DataFrame()
    
    df[column_name] = np.repeat(value,df.shape[0])
    return df


def get_time_related_df_columns(df):
    time_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    return time_columns



def export_df(df, out_file_name, columns=None, start_line=0, num_lines=None):
    """
    Exports a subset of a DataFrame to an Excel file.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    out_file_name (str): The name of the output Excel file.
    columns (list): List of columns to include in the export.
    start_line (int): The starting line (index) from which to export.
    num_lines (int): The number of lines (rows) to export.

    Returns:
    None
    """

    if (columns==None):
        columns = df.columns

    if (num_lines==None):
        num_lines = df.shape[0]
    # Select the desired subset of the DataFrame
    subset_df = df[columns].iloc[start_line:start_line+num_lines-1]
    print(subset_df.shape)
    
    # Export the subset to an Excel filez
    file_name, file_extension = os.path.splitext(out_file_name)

    print(f'exporting {num_lines} lines from df to {out_file_name}')

    if (file_extension=='.xlsx'):
        time_columns = get_time_related_df_columns(subset_df)

        for column in time_columns:
            subset_df.loc[:, column] = subset_df[column].dt.tz_localize(None)


        subset_df.to_excel(out_file_name, index=False)
        
    elif (file_extension=='.csv'):
        subset_df.to_csv(out_file_name, index=False)

def reorder_df_columns(df, order):
    """
    Reorder the columns of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame whose columns are to be reordered.
    order (list): A list specifying the desired order of columns. Columns not specified in the list will be appended at the end.

    Returns:
    pd.DataFrame: A DataFrame with columns reordered as specified.
    """
    # Ensure the columns in 'order' exist in the DataFrame
    order = [col for col in order if col in df.columns]

    # Get the remaining columns that are not in the 'order' list
    remaining_cols = [col for col in df.columns if col not in order]

    # Concatenate the specified columns with the remaining columns
    new_order = order + remaining_cols

    # Reorder the DataFrame columns
    return df[new_order]


def CheckColumnsInDF(df, columns):
    parse_parameter(lista.FlattenAList(columns),df.columns,'column')    

def handle_common_time_rows_in_df(df, time_column='time', ID_columns=[]):


    # handle a none list input 
    if (not isinstance(ID_columns,list)):
        ID_columns = [ID_columns]

    # Check if the specified columns exist in the DataFrame
    missing_columns = [col for col in ID_columns + [time_column] if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in DataFrame: {', '.join(missing_columns)}")
    
    # Initialize a counter for the number of common time chunks found
    common_time_chunks_count = 0
    
    # Get the total number of chunks
    total_chunks = df.groupby(ID_columns).ngroups
    
    # Function to handle rows with common time values in chunks defined by ID_columns
    def combine_rows(chunk, chunk_number):
        nonlocal common_time_chunks_count
        
        # Sort the chunk by the time_column
        chunk = chunk.sort_values(by=time_column)
        
        # Calculate the time differences in seconds
        time_diff = chunk[time_column].diff()
        # time_diff = time_diff_convert(time_diff, units='secs')
        zero_diff_line_numbers = np.where(time_diff == 0)[0]
        
        # Initialize a list to hold the indices of rows to be dropped
        indices_to_drop = []
        
        # Iterate over the indices with zero time differences and combine rows
        for line_number in zero_diff_line_numbers:
            # Ensure we have at least two rows to combine
            if line_number > 0:
                combined_row = chunk.iloc[line_number].combine_first(chunk.iloc[line_number - 1])
                
                # Place the combined row at the index of the first row in the group
                first_index = chunk.index[line_number - 1]
                df.loc[first_index] = combined_row
                
                # Add the index of the current row to the drop list
                indices_to_drop.append(chunk.index[line_number])
                
                common_time_chunks_count += 1  # Increment the counter
        
        # Drop the rows that have been combined
        if (len(indices_to_drop)!=0):
            df.drop(indices_to_drop, inplace=True)
            # df.loc[indices_to_drop, :] = df.drop(indices_to_drop)

            
        # Print progress every 1000 chunks
        if chunk_number % 10 == 0:
            print(f"Processed chunk {chunk_number} out of {total_chunks}")

    # Apply the function to each group defined by ID_columns
    for chunk_number, (_, chunk) in enumerate(df.groupby(ID_columns, group_keys=False), start=1):
        combine_rows(chunk, chunk_number)

    # print(f"Number of common time chunks found: {common_time_chunks_count}")
    
    return df


import pandas as pd

def pre_process_df_columns(df, **params):

    def update_df(df, column, processed_col,params,method):
        if params['add_modify'] == 'add':
            df[column + f'_{method}'] = processed_col
        else:
            df[column] = processed_col
        return df
    

    default_params = {
            'columns': None,        
            'pre_process_params': {'default': None},
            'add_modify': {'default': 'modify', 'optional': ['modify', 'add']},
        }

    try:
        params = parse_func_params(params, default_params)
    except ValueError as e:
        print(e)  # Print the exception message with calling stack path
        return None



    # Ensure columns is a list
    if isinstance(params['columns'], str):
        params['columns'] = [params['columns']]
    
    df_processed = df.copy()

    
    pre_process_params = params['pre_process_params']
    
    for method in pre_process_params.keys():
        method_params = pre_process_params[method]
        if 'columns' in method_params.keys():
            columns = method_params['columns']
        else:
            columns = params['columns']
        if method == 'span':
            for column in columns:
                processed_col = (df[column] - df[column].min()) / (df[column].max() - df[column].min()) * (method_params['val'][1] - method_params['val'][0]) + method_params['val'][0]
                df_processed = update_df(df_processed, column, processed_col,params,method)

        if (method == 'norm'):
            for column in columns:
                scaler = StandardScaler()
                processed_col = scaler.fit_transform(df[[column]])
                df_processed = update_df(df_processed, column, processed_col,params,method)


        elif method == 'unbias':
            for column in columns:
                processed_col = (df[column] - df[column].mean())
                df_processed = update_df(df_processed, column, processed_col,params,method)




    return df_processed

def add_order_column(df, column_name, order_list):
    """
    Adds an 'Order' column to the DataFrame based on the specified list order.

    Parameters:
    - df (pd.DataFrame): The DataFrame to which the 'Order' column will be added.
    - column_name (str): The name of the column in the DataFrame to be indexed (e.g., 'name').
    - order_list (list): The list of items defining the desired order.

    Returns:
    - pd.DataFrame: The DataFrame with the added 'Order' column.
    """
    # Create a mapping from the items in the order_list to their respective order
    order_mapping = {item: i + 1 for i, item in enumerate(order_list)}

    # Add the 'Order' column to the DataFrame based on the specified column
    df['order'] = df[column_name].map(order_mapping)

    # Optional: Handle any rows where the column value was not in the order_list
    # df['order'].fillna(len(order_list) + 1, inplace=True)  # Assign a high value to items not in the list, or handle as needed
    df['order'] = df['order'].fillna(len(order_list) + 1)  # Assign a high value to items not in the list, or handle as needed

    # Optionally sort the DataFrame by the 'Order' column
    df = df.sort_values('order').reset_index(drop=True)

    return df


def remove_time_duplicates(df, time_col='time', name_col='name'):
    
    # Convert the 'name' column to integer codes
    df[name_col + '_code'] = pd.Categorical(df[name_col]).codes
    
    # Create the new integer column combining 'time' and 'name'
    df['time_name_combined'] = df[time_col] * 1000 + df[name_col + '_code']
    
    # Sort the DataFrame by 'time_name_combined'
    df_sorted = df.sort_values(by='time_name_combined')
    

    
    # Drop duplicates while keeping the first occurrence
    df_unique = df_sorted.drop_duplicates(subset='time_name_combined', keep='first')
    
    # Drop the temporary columns
    # df_final = df_unique.drop(columns=[name_col + '_code', 'time_name_combined'])
    df_final = df_unique
    
    return df_final



def get_df_time_limits(df,time_column='time'):
    print((datenum2datetime(df[time_column].min()),datenum2datetime(df[time_column].max())))



def GetRowNumbersFromIndexList(df, index):
    """
    This function takes a DataFrame and a single index or list of indices, 
    and returns the corresponding row number(s).
    
    Parameters:
    - df: The pandas DataFrame.
    - index: A single index value or a list of index values.
    
    Returns:
    - A single row number (int) for a single index or a list of row numbers (list of int) for multiple indices.
      Returns None if an index is not found and prints a message.
    """
    index = converta.VarToList(index)   
    # If index is a list (multiple indices)
    if isinstance(index, list):
        row_nums = []
        for idx in index:
            if idx in df.index:
                row_nums.append(df.index.get_loc(idx))
            else:
                row_nums.append(None)
                print(f"Index {idx} not found in DataFrame.")
        return row_nums
    
    # If it's a single index
    else:
        if index in df.index:
            return df.index.get_loc(index)
        else:
            print(f"Index {index} not found in DataFrame.")
            return None

# to be removed, but check in Spoof
def IndexToRowNum(df, index):
    """
    This function takes a DataFrame and a single index or list of indices, 
    and returns the corresponding row number(s).
    
    Parameters:
    - df: The pandas DataFrame.
    - index: A single index value or a list of index values.
    
    Returns:
    - A single row number (int) for a single index or a list of row numbers (list of int) for multiple indices.
      Returns None if an index is not found and prints a message.
    """
    index = converta.VarToList(index)   
    # If index is a list (multiple indices)
    if isinstance(index, list):
        row_nums = []
        for idx in index:
            if idx in df.index:
                row_nums.append(df.index.get_loc(idx))
            else:
                row_nums.append(None)
                print(f"Index {idx} not found in DataFrame.")
        return row_nums
    
    # If it's a single index
    else:
        if index in df.index:
            return df.index.get_loc(index)
        else:
            print(f"Index {index} not found in DataFrame.")
            return None


import pandas as pd

import pandas as pd

def CompareDfs(df1, df2, to_print=True, ID_column='name'):
    """
    Compares two DataFrames based solely on the existence of values in a specific ID column
    and returns IDs that are unique to each DataFrame.

    Parameters:
        df1 (pd.DataFrame): The first DataFrame.
        df2 (pd.DataFrame): The second DataFrame.
        to_print (bool): If True, prints the unique IDs or equality message.
        ID_column (str): The column name to use as the ID for comparison.

    Returns:
        dict: A dictionary with two lists:
              'only_in_df1' - List of IDs in df1 but not in df2.
              'only_in_df2' - List of IDs in df2 but not in df1.
    """
    # Validate ID_column
    if ID_column is None:
        raise ValueError("ID_column must be provided for comparison.")
    if ID_column not in df1.columns or ID_column not in df2.columns:
        raise ValueError(f"Column '{ID_column}' must exist in both DataFrames.")
    
    # Find unique IDs in each DataFrame
    ids_only_in_df1 = df1[~df1[ID_column].isin(df2[ID_column])][ID_column].tolist()
    ids_only_in_df2 = df2[~df2[ID_column].isin(df1[ID_column])][ID_column].tolist()
    
    # Print based on conditions
    if to_print:
        if not ids_only_in_df1 and not ids_only_in_df2:
            print("DataFrames contain the same IDs.")
        else:
            if ids_only_in_df1:
                print("IDs only in df1:")
                for idx in ids_only_in_df1:
                    print(idx)
            if ids_only_in_df2:
                print("\nIDs only in df2:")
                for idx in ids_only_in_df2:
                    print(idx)
    
    return {
        'only_in_df1': ids_only_in_df1,
        'only_in_df2': ids_only_in_df2
    }

def ApplyFunctionOnSlidingWindow(df, column, function, N):
    """
    Apply a specified function on a sliding window over a DataFrame column.

    Parameters:
    - df: The input DataFrame
    - column: The name of the column on which to apply the function
    - function: The function to apply to each sliding window
    - N: The window size

    Returns:
    - A Series with the result of the function applied to each window
    """

    CheckColumnsInDF(df,columns = [column])

    return df[column].rolling(window=N).apply(function, raw=True)


import pandas as pd
import ast


def decode_dict_column_from_df(df, dic_column, mode='append'):
    def safe_eval(val):
        """Safely evaluates a string representation of a dictionary, handling numpy types."""
        try:
            # Replace numpy-specific float notation with standard float
            val = val.replace("np.float64(", "").replace(")", "")
            return ast.literal_eval(val)
        except Exception as e:
            return None

    """
    Decodes a dictionary column in a DataFrame into separate columns.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        dic_column (str): The name of the column containing dictionaries.
        mode (str): The mode of operation; 'append' to add new columns to the original DataFrame,
                    'separate_df' to return a new DataFrame with only the new columns.

    Returns:
        pd.DataFrame: The DataFrame with the decoded dictionary columns.
    """
    if dic_column not in df.columns:
        raise ValueError(f"Column '{dic_column}' not found in DataFrame.")

    # Convert the column values to dictionaries
    if (not isinstance(df[dic_column].iloc[0], dict)):
        df[dic_column] = df[dic_column].astype(str).apply(safe_eval)

    # Expand the dictionary column into separate columns
    expanded_cols = pd.json_normalize(df[dic_column])

    if mode == 'append':
        # Append the new columns to the original DataFrame
        result_df = pd.concat([df.drop(columns=[dic_column]), expanded_cols], axis=1)
    elif mode == 'separate_df':
        # Return only the new columns
        result_df = expanded_cols
    else:
        raise ValueError("Invalid mode. Choose either 'append' or 'separate_df'.")

    return result_df
