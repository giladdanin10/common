import pandas as pd
import time
from datetime import datetime, timedelta


def filter_df_by_date(df, min_date, max_date, time_column='Time', date_format='%Y-%m-%d %H:%M:%S'):
    """
    Function to filter a DataFrame based on a time column and specified date range.
    
    Parameters:
    
    
    - df (pd.DataFrame): The input DataFrame.
    - min_date (str): The minimum date as a string.
    - max_date (str): The maximum date as a string.
    - time_column (str): The name of the column containing time data in the specified format.
    - date_format (str): The format of the date strings in the time column and min_date, max_date.
    
    Returns:
    - filtered_df (pd.DataFrame): The DataFrame filtered by the specified date range.
    """
    # Convert the Time column to datetime
    df[time_column] = pd.to_datetime(df[time_column], format=date_format)

    if (min_date is None):
        min_date = min(df[time_column])

    if (max_date is None):
        max_date = max(df[time_column])


    
    # Convert min_date and max_date to datetime
    min_date = pd.to_datetime(min_date, format=date_format)
    max_date = pd.to_datetime(max_date, format=date_format)
    
    # Filter the DataFrame based on the date range
    filtered_df = df[(df[time_column] >= min_date) & (df[time_column] <= max_date)]
    
    return filtered_df


# Define the minimum and maximum dates
# min_date = '2023-02-01 00:00:01'
# max_date = '2023-02-02 00:00:01'

# # Filter the DataFrame based on the date range
# df = filter_df_by_date(df, min_date, max_date)

# get_min_max_dates(df)



def time_diff_convert(time_diff,units='mins',to_round=True):
    if (not isinstance(time_diff,pd.core.series.Series)):
        is_series = False
        time_diff = pd.Series(time_diff)
    else:
        is_series = True

    if (units == 'secs'):        
        time_diff_mod = time_diff.apply(lambda x: x.total_seconds()) 
    
    if (units == 'mins'):        
        time_diff_mod = time_diff.apply(lambda x: x.total_seconds() / 60) 

    if (units == 'hours'):        
        time_diff_mod = time_diff.apply(lambda x: x.total_seconds() / 3600) 

    if (to_round):
        time_diff_mod = round(time_diff_mod)

    if (not is_series):
        time_diff_mod = time_diff_mod.values[0]        
    return time_diff_mod
    

def datetime2datenum(date_num):
    def convert_to_unix(dt):
        """Convert datetime to Unix timestamp (seconds since epoch)."""
        return int(pd.to_datetime(dt).timestamp())

    if isinstance(date_num, (str, pd.Timestamp)):
        # Single value (string or timestamp)
        return convert_to_unix(date_num)
    
    elif isinstance(date_num, int):
        # Single integer (assumed to be already in Unix timestamp format)
        return date_num
    
    elif isinstance(date_num, list):
        if all(isinstance(x, int) for x in date_num):
            # List of integers (already Unix timestamps)
            return date_num
        elif all(isinstance(x, (str, pd.Timestamp)) for x in date_num):
            # List of strings or timestamps
            return [convert_to_unix(x) for x in date_num]
        else:
            raise ValueError("Unsupported data type in list")
        
    elif isinstance(date_num, tuple):
        if all(isinstance(x, int) for x in date_num):
            # Tuple of integers (already Unix timestamps)
            return date_num
        elif all(isinstance(x, (str, pd.Timestamp)) for x in date_num):
            # Tuple of strings or timestamps
            return tuple(convert_to_unix(x) for x in date_num)
        else:
            raise ValueError("Unsupported data type in tuple")
    
    elif isinstance(date_num, np.ndarray):
        if np.issubdtype(date_num.dtype, np.datetime64):
            # Array of datetime64 objects
            return np.array([convert_to_unix(x) for x in date_num])
        elif np.issubdtype(date_num.dtype, np.str_):
            # Array of strings
            return np.array([convert_to_unix(x) for x in date_num])
        elif np.issubdtype(date_num.dtype, np.int_):
            # Array of integers (already Unix timestamps)
            return date_num
        elif np.issubdtype(date_num.dtype, np.object_):
            # Array of pd.Timestamp objects (dtype object)
            return np.array([convert_to_unix(pd.Timestamp(x)) for x in date_num])
        else:
            raise ValueError("Unsupported NumPy array data type")
    
    elif isinstance(date_num, pd.Series):
        if pd.api.types.is_datetime64_any_dtype(date_num):
            # Series of datetime objects
            return date_num.apply(convert_to_unix)
        elif pd.api.types.is_string_dtype(date_num):
            # Series of strings
            return date_num.apply(convert_to_unix)
        elif pd.api.types.is_integer_dtype(date_num):
            # Series of integers (already Unix timestamps)
            return date_num
        else:
            raise ValueError("Unsupported Pandas Series data type")
    
    else:
        raise ValueError("Unsupported input type")

# # Example usage:
# # Single value
# print(datetime2datenum('2024-05-01 01:00:00'))
# print(datetime2datenum(pd.Timestamp('2024-05-01 01:00:00')))
# print(datetime2datenum(1719741600))  # Integer Unix timestamp

# # List of values
# print(datetime2datenum(['2024-05-01 01:00:00', '2024-05-01 02:00:00']))
# print(datetime2datenum([1719741600, 1719745200]))  # List of integers

# # NumPy array
# print(datetime2datenum(np.array(['2024-05-01 01:00:00', '2024-05-01 02:00:00'], dtype='str')))
# print(datetime2datenum(np.array([pd.Timestamp('2024-05-01 01:00:00'), pd.Timestamp('2024-05-01 02:00:00')])))
# print(datetime2datenum(np.array([1719741600, 1719745200])))  # NumPy array of integers

# # Pandas Series
# print(datetime2datenum(pd.Series(['2024-05-01 01:00:00', '2024-05-01 02:00:00'])))
# print(datetime2datenum(pd.Series([pd.Timestamp('2024-05-01 01:00:00'), pd.Timestamp('2024-05-01 02:00:00')])))
# print(datetime2datenum(pd.Series([1719741600, 1719745200])))  # Series of integers

import pandas as pd
import numpy as np

import pandas as pd
import numpy as np
import pytz

def datenum2datetime(time_num, time_zone=None):
    """
    Converts various input formats to datetime. Optionally applies a time zone.

    :param time_num: Input data (int, str, list, pd.Series, np.ndarray).
    :param time_zone: The time zone to apply. Default is None (no timezone conversion).
    :return: Datetime or series of datetimes with optional time zone conversion.
    """
    def convert_to_datetime(x):
        """Convert a single value to datetime."""
        if isinstance(x, (int, np.int64, float, np.float32, np.float64)):
            return pd.to_datetime(x, unit='s')  # Treat float as seconds since epoch
        elif isinstance(x, str):
            return pd.to_datetime(x)
        elif isinstance(x, pd.Timestamp):
            return x
        else:
            raise ValueError("Unsupported data type")
        

    # Function to apply timezone
    def apply_timezone(dt_series, time_zone):
        if time_zone:
            tz = pytz.timezone(time_zone)
            return dt_series.dt.tz_localize('UTC').dt.tz_convert(tz)
        return dt_series

    if isinstance(time_num, pd.Series):
        if pd.api.types.is_integer_dtype(time_num):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif pd.api.types.is_float_dtype(time_num):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif pd.api.types.is_datetime64_any_dtype(time_num):
            dt_series = time_num
        elif pd.api.types.is_string_dtype(time_num):
            dt_series = pd.to_datetime(time_num)
        else:
            raise ValueError("Unsupported data type in Series")
        return apply_timezone(dt_series, time_zone)

    elif isinstance(time_num, (int, np.int64, float, np.float32, np.float64)):
        dt = pd.to_datetime(time_num, unit='s')
        return apply_timezone(pd.Series([dt]), time_zone).iloc[0]
    
    elif isinstance(time_num, list):
        if all(isinstance(x, int) for x in time_num):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif all(isinstance(x, str) for x in time_num):
            dt_series = pd.to_datetime(time_num)
        else:
            raise ValueError("Unsupported data type in list")
        return apply_timezone(dt_series, time_zone)
    
    elif isinstance(time_num, str):
        dt = pd.to_datetime(time_num)
        return apply_timezone(pd.Series([dt]), time_zone).iloc[0]
    
    elif isinstance(time_num, np.ndarray):
        if np.issubdtype(time_num.dtype, np.int_):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif np.issubdtype(time_num.dtype, np.str_):
            dt_series = pd.to_datetime(time_num)
        elif np.issubdtype(time_num.dtype, np.datetime64):
            dt_series = pd.to_datetime(time_num)
        elif np.issubdtype(time_num.dtype, np.object_):
            dt_series = np.array([convert_to_datetime(x) for x in time_num])
            return apply_timezone(pd.Series(dt_series), time_zone)
        else:
            raise ValueError("Unsupported NumPy array data type")
        return apply_timezone(dt_series, time_zone)
    
    else:
        raise ValueError("Unsupported input type")


# Example usage:
# Single integer
# print(datenum2datetime(1719741600))

# # Series of integers
# print(datenum2datetime(pd.Series([1719741600, 1719745200])))

# # Series of datetime
# print(datenum2datetime(pd.Series([pd.Timestamp('2024-05-01 01:00:00'), pd.Timestamp('2024-05-01 02:00:00')])))

# # List of integers
# print(datenum2datetime([1719741600, 1719745200]))

# # Single string
# print(datenum2datetime('2024-05-01 01:00:00'))

# # List of strings
# print(datenum2datetime(['2024-05-01 01:00:00', '2024-05-01 02:00:00']))

# # NumPy array of integers
# print(datenum2datetime(np.array([1719741600, 1719745200])))

# # NumPy array of strings
# print(datenum2datetime(np.array(['2024-05-01 01:00:00', '2024-05-01 02:00:00'], dtype='str')))

# # NumPy array of datetime64
# print(datenum2datetime(np.array([pd.Timestamp('2024-05-01 01:00:00').to_datetime64(), pd.Timestamp('2024-05-01 02:00:00').to_datetime64()])))

# # NumPy array of objects (with pd.Timestamp)
# print(datenum2datetime(np.array([pd.Timestamp('2024-05-01 01:00:00'), pd.Timestamp('2024-05-01 02:00:00')], dtype=object)))
    

def convert_time_format(df, time_column, current_format, output_format):
    """
    Function to convert the time format of a specified column in a DataFrame.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - time_column (str): The name of the column containing time data.
    - current_format (str): The current format of the time data in the column.
    - output_format (str): The desired output format for the tim data.
    
    Returns:
    - df (pd.DataFrame): The DataFrame with the time column converted to the desired format.
    """
    # Convert the Time column to datetime using the current format
    df[time_column] = pd.to_datetime(df[time_column], format=current_format)
    
    # Convert the datetime to the desired output format
    df[time_column] = df[time_column].dt.strftime(output_format)
    
    return df




def get_min_max_dates(df, time_column='Time',input_format = '%Y-%m-%d %H:%M:%S',output_format='%Y-%m-%d %H:%M:%S'):
    """
    Function to get the minimum and maximum dates from a DataFrame's time column.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame.
    - time_column (str): The name of the column containing time data in '%Y-%m-%d %H:%M:%S' format.
    - output_format (str): The desired output datetime format.
    
    Returns:
    - min_date (str): The minimum date in the desired format.
    - max_date (str): The maximum date in the desired format.
    """
    # # Convert the Time column to datetime
    # df[time_column] = pd.to_datetime(df[time_column], format=input_format)
    
    if (df.shape[0] == 0):
        print("Empty DataFrame")  
        return None,None
    
    # Get the minimum and maximum dates
    time_data = pd.to_datetime(df[time_column])
    min_date = time_data.min().strftime(output_format)
    max_date = time_data.max().strftime(output_format)
    
    return min_date, max_date



# # Get the minimum and maximum dates in the desired format
# min_date, max_date = get_min_max_dates(df)

# print("Min date:", min_date)
# print("Max date:", max_date)


# Tic function to start timing
def tic():
    global start_time
    start_time = time.time()

# Toc function to stop timing and print the elapsed time
def toc():
    if 'start_time' in globals():
        elapsed_time = time.time() - start_time
        print(f"Elapsed time: {elapsed_time:.6f} seconds")
    else:
        print("Tic has not been called yet!")


def get_time_scale(start_time, end_time, diff_unit):
    """
    Generates a list of intermediate times between start_time and end_time, based on diff_unit.

    :param start_time: The start time as a string (format: 'YYYY-MM-DD HH:MM:SS').
    :param end_time: The end time as a string (format: 'YYYY-MM-DD HH:MM:SS').
    :param diff_unit: The difference unit in hours (e.g., 1 for 1 hour, 1.5 for 1.5 hours, 24 for 1 day).
    :return: A list of intermediate times (as strings) between start_time and end_time.
    """

    # Convert start_time and end_time strings to datetime objects
    start_time_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    # Calculate the timedelta based on the diff_unit in hours
    time_delta = timedelta(hours=diff_unit)

    # Generate the intermediate times
    time_scale = []
    current_time = start_time_dt

    while current_time <= end_time_dt:
        time_scale.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))
        current_time += time_delta

    return time_scale