
import pandas as pd
import numpy as np

def convert_to_float(s):
    """
    Convert a string representation of a number in exponential format to a float.
    
    Parameters:
    - s: String containing the number in exponential format or a float.
    
    Returns:
    - Float representation of the number.
    """
    try:
        if isinstance(s, float):
            return s
        elif isinstance(s, str):
            # Check if the string contains a decimal point in the exponent part
            if 'E+' in s or 'E-' in s or 'e+' in s or 'e-' in s:
                parts = s.split('E') if 'E' in s else s.split('e')
                
                # Extract the base number and exponent
                base = float(parts[0])
                exponent = float(parts[1])
                
                # Adjust exponent if it contains a decimal point
                if '.' in parts[1]:
                    exponent = int(float(parts[1]))  # Convert to int to remove decimal part
                
                # Calculate the final float value
                result = base * (10 ** exponent)
                
                return result
            
            # If no 'E' or 'e' found, convert directly to float
            return float(s)
        
    except ValueError as e:
        print(f"Error converting '{s}' to float: {e}")
        return None


def convert_time_column(df: pd.DataFrame, time_column: str) -> pd.DataFrame:
    """
    Converts the specified time column to datetime if it is of type object.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing the time column.
    time_column (str): The name of the time column to convert.
    
    Returns:
    pd.DataFrame: The DataFrame with the converted time column.
    """
    if df[time_column].dtype == 'O':  # 'O' stands for object
        df[time_column] = pd.to_datetime(df[time_column])
    return df


def VarToList(var):
    # If it's already a list, return as-is
    if isinstance(var, list):
        return var
    # If it's a string, wrap it in a list
    elif isinstance(var, str):
        return [var]
    # If it's a Pandas Series, convert to a list
    elif isinstance(var, pd.Series):
        return var.tolist()
    # If it's a Pandas Index, convert to a list
    elif isinstance(var, pd.Index):
        return var.tolist()
    # If it's a NumPy array, convert to a list
    elif isinstance(var, np.ndarray):
        return var.tolist()
    # If it's anything else, wrap it in a list
    else:
        return [var]

