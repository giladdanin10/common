import pandas as pd
import time
from datetime import datetime, timedelta
from pandas._libs.tslibs.timestamps import Timestamp
import pytz
import sys

def datestr2datetime(date_str, format="%Y-%m-%d %H:%M:%S", time_zone=None):
    """
    Converts a date string to a datetime object if the input is a string, with optional timezone and format.
    
    :param date_str: The date string to convert.
    :param format: The format of the date string. Default is "%Y-%m-%d %H:%M:%S".
    :param time_zone: Optional timezone to localize the datetime. Default is None (no timezone).
    :return: A formatted datetime string with timezone applied if specified; otherwise, None.
    """
    if isinstance(date_str, str):
        try:
            # Truncate microseconds to six digits if needed
            if "%f" in format and "." in date_str:
                main_part, microseconds = date_str.split(".")
                date_str = f"{main_part}.{microseconds[:6]}"
            
            # Convert to datetime
            dt = datetime.strptime(date_str, format)
            
            # Apply timezone if specified
            if time_zone:
                tz = pytz.timezone(time_zone)
                dt = dt.replace(tzinfo=pytz.UTC).astimezone(tz)
            
            # Format datetime output
            return dt.strftime(format)
        except ValueError:
            print('Error: string does not match format')
            sys.exit(1)  # Exit with an error code
    else:
        return date_str


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

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pytz


def datetime2datestr(dt, format="%Y-%m-%d %H:%M:%S"):
    """
    Converts a datetime object to a formatted date string.

    :param dt: The datetime object to convert.
    :param format: The format for the output date string. Default is "%Y-%m-%d %H:%M:%S".
    :return: A formatted date string, or None if the input is not a datetime object.
    """
    if isinstance(dt, (datetime, pd.Timestamp)):
        return dt.strftime(format)
    else:
        print("Error: Input is not a datetime or Timestamp object.")
        return None


def datenum2datetime(time_num, time_zone=None, format="%Y-%m-%d %H:%M:%S"):
    """
    Converts various input formats to datetime. Optionally applies a time zone.

    :param time_num: Input data (int, str, list, pd.Series, np.ndarray).
    :param time_zone: The time zone to apply. Default is None (no timezone conversion).
    :param format: The format for input date strings. Default is "%Y-%m-%d %H:%M:%S".
    :return: Datetime or series of datetimes with optional time zone conversion.
    """
    def convert_to_datetime(x):
        """Convert a single value to datetime."""
        if isinstance(x, (pd.Timestamp, datetime)):
            return x
        elif isinstance(x, (int, np.integer, float, np.floating)):
            return pd.to_datetime(x, unit='s')
        elif isinstance(x, str):
            return pd.to_datetime(x, format=format)
        elif isinstance(x, pd.Series):
            return pd.to_datetime(x)
        else:
            raise ValueError(f"Unsupported data type: {type(x)}")

    def apply_timezone(dt_series, time_zone):
        """Apply timezone to datetime series or single Timestamp."""
        if time_zone:
            tz = pytz.timezone(time_zone)
            if isinstance(dt_series, pd.Series):
                return dt_series.dt.tz_localize('UTC').dt.tz_convert(tz)
            else:  # Handle individual Timestamp or datetime
                return dt_series.tz_localize('UTC').tz_convert(tz)
        return dt_series

    # Handle Pandas Series
    if isinstance(time_num, pd.Series):
        if pd.api.types.is_numeric_dtype(time_num):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif pd.api.types.is_datetime64_any_dtype(time_num):
            dt_series = time_num
        elif pd.api.types.is_string_dtype(time_num):
            dt_series = pd.to_datetime(time_num, format=format)
        else:
            raise ValueError("Unsupported data type in Series")
        return apply_timezone(dt_series, time_zone)

    # Handle individual numeric values
    elif isinstance(time_num, (int, np.integer, float, np.floating)):
        dt = pd.to_datetime(time_num, unit='s')
        return apply_timezone(dt, time_zone)

    # Handle lists
    elif isinstance(time_num, list):
        if all(isinstance(x, int) for x in time_num):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif all(isinstance(x, str) for x in time_num):
            dt_series = pd.to_datetime(time_num, format=format)
        else:
            raise ValueError("Unsupported data type in list")
        return apply_timezone(dt_series, time_zone)

    # Handle string inputs
    elif isinstance(time_num, str):
        dt = pd.to_datetime(time_num, format=format)
        return apply_timezone(dt, time_zone)

    # Handle NumPy arrays
    elif isinstance(time_num, np.ndarray):
        if np.issubdtype(time_num.dtype, np.integer) or np.issubdtype(time_num.dtype, np.floating):
            dt_series = pd.to_datetime(time_num, unit='s')
        elif np.issubdtype(time_num.dtype, np.str_):
            dt_series = pd.to_datetime(time_num, format=format)
        elif np.issubdtype(time_num.dtype, np.datetime64):
            dt_series = pd.to_datetime(time_num)
        elif np.issubdtype(time_num.dtype, np.object_):
            dt_series = np.array([convert_to_datetime(x) for x in time_num])
            return apply_timezone(pd.Series(dt_series), time_zone)
        else:
            raise ValueError("Unsupported NumPy array data type")
        return apply_timezone(dt_series, time_zone)

    # Handle individual datetime or Timestamp objects directly
    elif isinstance(time_num, (pd.Timestamp, datetime)):
        return apply_timezone(time_num, time_zone)

    else:
        raise ValueError(f"Unsupported input type: {type(time_num)}")
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




def get_min_max_dates(df, time_column='time',input_format = '%Y-%m-%d %H:%M:%S',output_format='%Y-%m-%d %H:%M:%S'):
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
    if pd.api.types.is_integer_dtype(df[time_column]) or pd.api.types.is_float_dtype(df[time_column]):
        min_date = datenum2datetime(df[time_column].min())
        max_date = datenum2datetime(df[time_column].max())        
    else:
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


import pandas as pd
import numpy as np
from datetime import datetime

def MatchTimeFormat(var1, var2, adjust_lengths=False):
    """
    Converts var2 to match the format of var1 (ISO 8601 format with 'T').
    
    Parameters:
    - var1: A string, list, NumPy array, or Pandas Series in ISO 8601 format.
    - var2: A string, list, NumPy array, Pandas Series, or Timestamp in a different datetime format.
    - adjust_lengths: Boolean to indicate whether to adjust lengths (default=False).
    
    Returns:
    - var2 converted to match var1's format.
    
    Raises:
    - ValueError if var1 or var2 is not in a valid datetime format.
    - ValueError if var1 and var2 have different lengths when passed as lists or Series and `adjust_lengths=False`.
    """
    
    # Helper function to handle individual string conversion
    def convert_single(var1_str, var2_str):
        # Convert var1_str to a datetime object (ISO 8601)
        try:
            var1_datetime = datetime.fromisoformat(var1_str.replace('Z', ''))
        except ValueError:
            raise ValueError(f"var1 value '{var1_str}' is not a valid ISO 8601 datetime format.")
        
        # Convert var2_str or Timestamp to a datetime object
        if isinstance(var2_str, pd.Timestamp):
            var2_datetime = var2_str
        else:
            var2_truncated = var2_str[:26]  # Truncate var2 to 6-digit microseconds
            try:
                var2_datetime = datetime.strptime(var2_truncated, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                raise ValueError(f"var2 value '{var2_str}' is not in a valid datetime format.")
        
        # Preserve the full precision for microseconds if var2_str is a string and longer than 6 digits
        extra_digits = ''
        if isinstance(var2_str, str) and len(var2_str) > 26:
            extra_digits = var2_str[26:]  # Keep the extra digits
        
        # Format var2_str to match var1's format (ISO 8601 with 'T')
        var2_formatted = var2_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + extra_digits
        
        return var2_formatted

    # Handle NumPy arrays by converting them to lists
    if isinstance(var1, np.ndarray):
        var1 = var1.tolist()
    if isinstance(var2, np.ndarray):
        var2 = var2.tolist()
    
    # If var2 is a single Timestamp and var1 is iterable (list, np.array, or pd.Series)
    if isinstance(var2, pd.Timestamp) and isinstance(var1, (list, pd.Series, np.ndarray)):
        var2 = [var2] * len(var1)

    # If var1 is a single Timestamp and var2 is iterable
    if isinstance(var1, pd.Timestamp) and isinstance(var2, (list, pd.Series, np.ndarray)):
        var1 = [var1] * len(var2)

    # If inputs are lists or Pandas Series
    if isinstance(var1, (list, pd.Series)) and isinstance(var2, (list, pd.Series)):
        # If adjust_lengths is True, adjust lengths of var1 and var2
        if adjust_lengths:
            max_len = max(len(var1), len(var2))
            var1 = var1 + [None] * (max_len - len(var1)) if len(var1) < max_len else var1[:max_len]
            var2 = var2 + [None] * (max_len - len(var2)) if len(var2) < max_len else var2[:max_len]
        else:
            # Ensure both inputs have the same length
            if len(var1) != len(var2):
                raise ValueError(f"var1 and var2 must have the same length. Got lengths {len(var1)} and {len(var2)}.")
        
        # Convert each pair of var1 and var2 elements
        return [convert_single(v1, v2) if v1 and v2 else None for v1, v2 in zip(var1, var2)]
    
    # If inputs are single strings or Timestamps
    elif isinstance(var1, str) and isinstance(var2, (str, pd.Timestamp)):
        return convert_single(var1, var2)
    
    else:
        raise ValueError("var1 and var2 must be both strings, lists, NumPy arrays, or Pandas Series.")

# # Example usage:

# # For single string and Pandas Timestamp inputs
# var1_single = "2024-04-01T08:50:59.926000118"
# var2_single_timestamp = pd.Timestamp("2024-04-01 08:31:59.926000118")
# print("Single Input (Timestamp):", MatchTimeFormat(var1_single, var2_single_timestamp))

# # For NumPy array and list inputs
# var1_array = np.array(["2024-04-01T08:50:59.926000118", "2024-04-01T08:50:59.926000118"])
# var2_list = ["2024-04-01 08:31:59.926000118", "2024-04-01 08:32:59.926000118"]
# print("NumPy Array and List Input:", MatchTimeFormat(var1_array, var2_list))

# # For Pandas Series and single Pandas Timestamp
# var1_series = pd.Series(["2024-04-01T08:50:59.926000118", "2024-04-01T08:50:59.926000118"])
# var2_single_timestamp = pd.Timestamp("2024-04-01 08:31:59.926000118")
# print("Series and Single Timestamp Input:", MatchTimeFormat(var1_series, var2_single_timestamp))
