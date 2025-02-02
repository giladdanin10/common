import sys
from pathlib import Path
import os
import pickle
import pandas as pd


algo_path = Path(r'C:\work\code\AIS-R-D\algo')
sys.path.append(str(algo_path))


import os
import pandas as pd
import pickle
from parse_aux import *
from str_aux import *



def load_or_create_df(csv_file_path, save_path,reload = False):
    if os.path.exists(save_path) and reload==False:
        print(f"Loading DataFrame from {save_path}")
        df = pd.read_pickle(save_path)
    else:
        print(f"Reading CSV file from {csv_file_path}")
        df = pd.read_csv(csv_file_path, low_memory=False)
        print(f"Saving DataFrame to {save_path}")
        df.to_pickle(save_path)
    return df


def load_df_from_file(file_name):
    print(f'load df from {file_name}')
    try:
        with open(file_name, 'rb') as file:
            var = pd.read_pickle(file)
        return var
    except Exception as e:
        print(f'could not load df from {file_name}. Error: {e}')
        return None


import os
import pickle
import pandas as pd
import numpy as np
from pathlib import Path

def get_file_name_extension(file_name):
    return Path(file_name).suffix[1:]  # Remove the leading dot

def save_var(var, file_name, var_name='var'):
    file_ext = get_file_name_extension(file_name)
    print(f'Saving {var_name} to {file_name}')
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        if file_ext == 'pkl':  
            # Save the variable to a pickle file
            with open(file_name, 'wb') as file:
                pickle.dump(var, file)
            return True
        
        elif file_ext == 'csv':
            # Handle DataFrame
            if isinstance(var, pd.DataFrame):
                var.to_csv(file_name, index=False, float_format='%.8f')  # Adjust precision if needed
            
            # Handle NumPy array
            elif isinstance(var, np.ndarray):
                # Check if the array contains only integers
                if np.issubdtype(var.dtype, np.integer):
                    np.savetxt(file_name, var, delimiter=',', fmt='%d')  # Use integer format
                else:
                    np.savetxt(file_name, var, delimiter=',', fmt='%.8f')  # Use floating-point format
            
            # Handle lists (converting to DataFrame first)
            elif isinstance(var, list):
                df = pd.DataFrame(var)
                # Determine if the DataFrame contains only integers
                if df.applymap(np.isreal).all().all() and df.applymap(float.is_integer).all().all():
                    df.to_csv(file_name, index=False, header=False, float_format='%d')  # Use integer format
                else:
                    df.to_csv(file_name, index=False, header=False, float_format='%.8f')  # Use floating-point format
            
            else:
                print(f'Unsupported variable type for CSV: {type(var)}')
                return False
            
            return True

        else:
            print(f'Unsupported file extension: {file_ext}')
            return False

    except Exception as e:
        print(f'Could not save {var_name} to {file_name}. Error: {e}')
        return False


def load_var(file_name, var_name='var'):
    print(f'load {var_name} from {file_name}')
    try:
        with open(file_name, 'rb') as file:
            var = pickle.load(file)
        return var
    except Exception as e:
        print(f'could not load {var_name} from {file_name}. Error: {e}')
        return None
    




def get_file_base_name(file_path):
    # Get the file name from the path
    file_name = os.path.basename(file_path)
    # Split the file name and extension
    file_base, _ = os.path.splitext(file_name)
    return file_base

def get_file_name_extension (file_name):
    return Path(file_name).suffix


def save_var(var, file_name, var_name='var'):
    print(f'save {var_name} to {file_name}')
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        # Save the variable to the file
        with open(file_name, 'wb') as file:
            pickle.dump(var, file)
        return True
    except Exception as e:
        print(f'could not save {var_name} to {file_name}. Error: {e}')
        return False






def load_folder_files_to_df(**params):


    default_params = {
        'input_folder': None,
        'output_folder': None,
        'file_name_filter': None,
        'file_ext': {'default': '.csv'},'optional': ['.csv', '.xlsx'],
        'force_reload': False
        }


    try:
        params = parse_func_params(params, default_params)
    except ValueError as e:
        print(e)  # Print the exception message with calling stack path
        return None

    if (params['output_folder'] is None):
        params['output_folder'] = params['input_folder']

    check_none_keys(params,['input_folder'])   
    input_folder = params['input_folder']
    output_folder = params['output_folder']
    file_name_filter = params['file_name_filter']
    file_ext = params['file_ext']
    force_reload = params['force_reload']

    # Initialize or load the accumulated DataFrame and loaded files list
    df_file_path = os.path.join(output_folder, 'df.pkl')
    loaded_files_path = os.path.join(output_folder, 'loaded_files.pkl')
    
    if force_reload:
        accumulated_df = pd.DataFrame()
        loaded_files = []   
    else:
        if os.path.exists(df_file_path):
            accumulated_df, _ = load_var(df_file_path, 'accumulated_df')
        else:
            accumulated_df = pd.DataFrame()

        if os.path.exists(loaded_files_path):
            loaded_files, _ = load_var(loaded_files_path, 'loaded_files')
        else:
            loaded_files = []

    # List all files in the input folder
    files_to_load = [f for f in os.listdir(input_folder) 
                     if os.path.isfile(os.path.join(input_folder, f)) and 
                     (not file_ext or f.endswith(file_ext)) and
                     (not file_name_filter or file_name_filter in f)]

    # Remove already loaded files
    files_to_load = [f for f in files_to_load if f not in loaded_files]

    total_files = len(files_to_load)
    for i, file_name in enumerate(files_to_load):
        print(f"load {file_name} ({i+1} out of {total_files})")
        
        # Load the file into a DataFrame and concatenate it with the accumulated DataFrame
        file_path = os.path.join(input_folder, file_name)
        try:
            if file_ext == '.csv':
                file_df = pd.read_csv(file_path)
            elif file_ext == '.xlsx':
                pd.read_excel(file_path)
            
            accumulated_df = pd.concat([accumulated_df, file_df], ignore_index=True)
        except Exception as e:
            print(f'could not load file {file_name}. Error: {e}')
            continue
        
        # Add the file to the loaded files list
        loaded_files.append(file_name)
    
        # Save the accumulated DataFrame and loaded files list
        save_var(accumulated_df, df_file_path, 'accumulated_df')
        save_var(loaded_files, loaded_files_path, 'loaded_files')

    return accumulated_df
# Example usage:
# load_folder_files_to_df(input_folder='path/to/input/folder', output_folder='path/to/output/folder', file_name_filter='filter_string', file_ext='.csv')


def prepare_file_path(file_path: str) -> str:
    """
    Replaces single slashes with double slashes in a file path.
    
    Parameters:
    file_path (str): The original file path.
    
    Returns:
    str: The file path with single slashes replaced by double slashes.
    """

    file_path.replace('/', '//')
    file_path.replace('\\', '//')
    return file_path
    return 


def get_folder_files(in_folder, str_filter=None):
    # List all files in the folder
    all_files = [f for f in os.listdir(in_folder) if os.path.isfile(os.path.join(in_folder, f))]
    
    # Apply the string filter to the list of files
    filtered_files = filter_strs(all_files, str_filter)
    
    return filtered_files


def add_directories_to_sys_path(top_directory: Path):
    """
    Recursively add all directories under the top_directory to sys.path.

    Args:
        top_directory (Path): The top-level directory to start the recursion.
    """
    for directory in top_directory.rglob('*'):
        if directory.is_dir():
            sys.path.append(str(directory))



import os
import sys
def AddToSysPath(file_path):
    """
    Add the directory of the given relative or absolute file path to sys.path for module importing.

    Args:
        file_path (str): The relative or absolute path of the directory or file.
    """
    # Convert the relative path to an absolute path
    abs_path = os.path.abspath(file_path)
    
    # Check if the absolute directory path is already in sys.path
    if abs_path not in sys.path:
        sys.path.append(abs_path)
        print(f"Directory '{abs_path}' added to sys.path.")
    else:
        print(f"Directory '{abs_path}' is already in sys.path.")


import os

def FindRelativePath(file1, file2, format='explorer'):
    """
    Finds the relative path from file1 to file2 and formats it according to the specified format.

    Args:
        file1 (str): The absolute path of the first file.
        file2 (str): The absolute path of the second file.
        format (str): The format of the output path. Options are 'explorer' (default) and 'import'.
                      'explorer' uses standard path format, and 'import' converts the path into a relative import path.

    Returns:
        str: The relative path from file1 to file2, formatted as specified.
    """
    # Get the directory path of both files
    dir1 = os.path.dirname(os.path.abspath(file1))
    dir2 = os.path.dirname(os.path.abspath(file2))
    
    # Compute the relative path
    relative_path = os.path.relpath(dir2, dir1)
    

    if os.path.isdir(file1):
        relative_path = os.path.join('..',relative_path)


    # If the format is 'import', switch the slashes and format with '..' for relative import
    if format == 'import':
        relative_path = relative_path.replace(os.path.sep, '.')  # Replace file separators with dots
        # Remove any leading dot characters (if present), as Python relative imports use leading '..'
        relative_path = relative_path.replace('..', '').lstrip('.')

    return relative_path

# # Example usage:
# file1 = r'C:\work\code\algo-dayrun\utilities\SQL\PostgreSQL'
# file2 = r'C:\work\code\algo-dayrun\src\test\spoofing_algo\Vessels.py'

# relative_path = FindRelativePath(os.getcwd(), r'C:\work\code\algo-dayrun\src\test\spoofing_algo\Vessels.py')
# print(f"The relative path from file1 to file2 is: {relative_path}")

def CopyFile(source_path, destination_path):
    """
    Copy a file from the source path to the destination path.

    Args:
        source_path (str): The path of the source file to be copied.
        destination_path (str): The path of the destination file to copy to.

    Returns:
        bool: True if the file was copied successfully, False otherwise.
    """
    try:
        with open(source_path, 'rb') as source_file:
            with open(destination_path, 'wb') as destination_file:
                destination_file.write(source_file.read())
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
source_path = Path("path/to/source/file.txt")
destination_path = Path("path/to/destination/file.txt")

try:
    destination_path.write_bytes(source_path.read_bytes())
    print("File copied successfully.")
except FileNotFoundError:
    print("The source file does not exist.")
except PermissionError:
    print("Permission denied. Check your access rights.")
except Exception as e:
    print(f"An error occurred: {e}")



def get_workspace_root():
    # Start from the current notebook's directory
    current_dir = Path.cwd()

    # Walk up the directory tree to find the workspace root
    for parent in current_dir.parents:
        if (parent / ".git").exists() or (parent / "workspace.code-workspace").exists():
            workspace_root = parent
            break
    else:
        workspace_root = current_dir  # Default to the notebook directory

    return str(workspace_root)

